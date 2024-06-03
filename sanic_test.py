from sanic import Sanic
from sanic.response import json
from datetime import datetime
import multiprocessing

app = Sanic("SanicAPP")
HOST = "localhost"
PORT = 8000

app.config.FALLBACK_ERROR_FORMAT = 'json'
app.config.ACCESS_LOG = True


async def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route('/getdatetime')
async def getdatetime(request):
    return json({"now": await get_datetime(), 'server_name': request.server_name, 'path': request.path})


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False, auto_reload=True, workers=multiprocessing.cpu_count() // 5)
