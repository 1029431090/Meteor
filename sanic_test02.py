import datetime
from sanic import Sanic, response
from sqlalchemy import create_engine, or_, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import LONGTEXT, DOUBLE

app = Sanic(__name__)

engine = create_engine("mysql+pymysql://root:123456789@127.0.0.1:3306/xapi", echo=True, future=True, pool_use_lifo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class MeteorTest(Base):
    __tablename__ = "meteor_test"
    id = Column(Integer, primary_key=True, comment="ID", autoincrement=True)
    filename = Column(String(255), comment="文件名")
    content = Column(LONGTEXT, comment="文件内容")
    tran_content = Column(LONGTEXT, comment="文件内容翻译")
    m_fm = Column(String(255), comment="主节点")
    m_to = Column(String(255), comment="从节点")
    m_lat = Column(DOUBLE, comment="纬度")
    m_lon = Column(DOUBLE, comment="经度")
    m_time = Column(DateTime, comment="时间")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

async def init_data():
    async with SessionLocal() as session:
        items = [
            {
                "id": 4,
                "filename": "ddd.txt",
                "content": "promote中打开conda environment,并查看conda环境信息 conda info--envs 1 打开后可以看 到下",
                "tran_content": "如我这个anaconda3.7下的是conda4.5.6,而anaconda2023是最新版的conda环境",
                "m_fm": "DD",
                "m_to": "EE",
                "m_lat": 40.231,
                "m_lon": 116.358,
                "m_time": datetime.datetime.strptime("2024-05-30 20:12:13", "%Y-%m-%d %H:%M:%S"),
            },
            # 添加其他数据项
        ]

        for item in items:
            meteor = await session.execute(MeteorTest.query.filter_by(id=item["id"]))
            meteor = meteor.scalar()

            if meteor:
                continue

            meteor = MeteorTest(
                id=item["id"],
                filename=item["filename"],
                content=item["content"],
                tran_content=item["tran_content"],
                m_fm=item["m_fm"],
                m_to=item["m_to"],
                m_lat=item["m_lat"],
                m_lon=item["m_lon"],
                m_time=item["m_time"],
            )

            session.add(meteor)

        await session.commit()

@app.get("/")
async def hello_world(request):
    return response.json({"code": 200, "msg": "Hello world!"})

@app.get("/api/meteors/")
async def query(request):
    target = request.args.get("target")
    date_min = request.args.get("date_min")
    date_max = request.args.get("date_max")
    
    async with SessionLocal() as session:
        if not date_min and not date_max:
            date_min = datetime.datetime.today().strftime("%Y-%m-%d")
            date_max = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        query = []
        if target:
            query.append(or_(MeteorTest.m_fm == target, MeteorTest.m_to == target))
        if date_min:
            query.append(MeteorTest.m_time >= datetime.datetime.strptime(date_min, "%Y-%m-%d"))
        if date_max:
            query.append(MeteorTest.m_time < datetime.datetime.strptime(date_max, "%Y-%m-%d"))
    
        meteors = await session.execute(MeteorTest.query.filter(*query))
        meteors = meteors.scalars().all()

        _meteors = []
        for meteor in meteors:
            _meteor = meteor.to_dict()
            for key in ["m_lat", "m_lon"]:
                _meteor[key] = round(float(str(_meteor[key])), 3)

            _meteor["source"] = _meteor.pop("m_fm", None)
            _meteor["target"] = _meteor.pop("m_to", None)

            _meteors.append(_meteor)

        return response.json({"code": 200, "data": _meteors})

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.add_task(init_data())
    app.run(host="0.0.0.0", port=8000)
