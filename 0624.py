import datetime
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
import pymysql

app = Sanic("SanicAPP")
CORS(app, supports_credentials=True)

HOST = "localhost"
PORT = 3060

app.config.FALLBACK_ERROR_FORMAT = "json"
app.config.ACCESS_LOG = True


async def get_data(request):
    target = request.args.get("target")
    date_min = request.args.get("date_min")
    date_max = request.args.get("date_max")

    db = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="1qazxsw2#EDC",
        database="sys")
    cursor = db.cursor()

    if not date_min and not date_max and not target:
        date_min = datetime.datetime.today().strftime("%Y-%m-%d")
        date_max = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        sql = f"select * from `meteor_test` where m_time>'{date_min}' and m_time<'{date_max}';"
    elif not target:
        sql = f"select * from `meteor_test` where m_time>'{date_min}' and m_time<'{date_max}';"
    else:
        sql = f"select * from `meteor_test` where m_time>'{date_min}' and m_time<'{date_max}' and m_fm='{target}'" \
              f"or m_time>'{date_min}' and m_time<'{date_max}' and m_to='{target}';"

    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()

    final_result = {"code": 200, "data": []}

    for row in results:
        row_dict = dict(zip([col[0] for col in cursor.description], row))
        final_result["data"].append(
            {
                "id": row_dict["id"],
                "filename": row_dict["filename"],
                "content": row_dict["content"],
                "tran_content": row_dict["tran_content"],
                "m_lat": row_dict["m_lat"],
                "m_lon": row_dict["m_lon"],
                "m_time": str(row_dict["m_time"]),
                "source": row_dict["m_fm"],
                "target": row_dict["m_to"],
            }
        )
    return final_result


@app.get('/api/meteors')
async def getdata(request):
    data = await get_data(request)
    return json(data)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False, auto_reload=True, workers=1)
