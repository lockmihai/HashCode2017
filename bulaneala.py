import sys
import os
import time
from random import randint, randrange

stderr = sys.stdout
parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, parent_dir)

num_vid = 0
num_endpoints = 0
num_req = 0
num_server = 0
capacity = 0

videos = []
endpoints = []
servers = []


def read_data(input):
    global videos
    global endpoints
    global servers
    global num_vid
    global num_endpoints
    global num_req
    global num_server
    global capacity
    num_vid, num_endpoints, num_req, num_server, capacity = map(int, input.readline().split())

    videos = list(map(int, input.readline().split()))

    for i in range(num_server):
        servers.append({
            "videos": {},
            "endpoints": []
        })

    for i in range(num_endpoints):
        lat, nr = map(int, input.readline().split())

        # conn = []
        # for j in range(nr):
        #     point, lat_point = map(int, input.readline().split())
        #     conn.append({
        #         "latency": lat_point,
        #         "id_server": point
        #     })
        conn = {}
        lat_min = lat
        id_min = -1
        for j in range(nr):
            id_server, lat_server = map(int, input.readline().split())
            if lat_server < lat_min:
                lat_min = lat_server
                id_min = id_server
            conn[id_server] = lat_server
            servers[id_server]["endpoints"].append(i)
        endpoints.append({
            "latency": lat,
            "servers": conn,
            "best_server": id_min,
            "req": {},
            "attrib": {}
        })

    max_nr = 0
    for i in range(num_req):
        video, point, nr = map(int, input.readline().split())
        endpoint = endpoints[point]
        if video not in endpoint["req"]:
            endpoint["req"][video] = 0
        endpoint["req"][video] += nr

        if nr * 1.1 < max_nr:
            continue
        if nr > max_nr:
            max_nr = nr
        id_server = endpoint["best_server"]
        if id_server == -1:
            continue
        if len(servers[id_server]["videos"]) < 6:
            servers[id_server]["videos"][video] = {}
        # for serv in endpoints[point]["servers"]:
        #     reducere[serv][video] +=


def initialize():
    viz = [0 for j in range(num_vid)]
    for id_server in range(num_server):
        serv = servers[id_server]
        vid_data = [{"count": 0, "reducere": 0} for j in range(num_vid)]
        for id_point in serv["endpoints"]:
            for id_video in endpoints[id_point]["req"]:
                vid_data[id_video]["id"] = id_video
                vid_data[id_video]["count"] += endpoints[id_point]["req"][id_video]
                latency_diff = (endpoints[id_point]["latency"] - endpoints[id_point]["servers"][id_server])
                vid_data[id_video]["reducere"] += latency_diff * endpoints[id_point]["req"][id_video]

        vid_touples = []
        for data in vid_data:
            if data["count"] == 0:
                continue
            vid_touples.append((data["id"], data["count"], data["reducere"]))

        vid_touples.sort(key=lambda chestie: chestie[2] / (videos[chestie[0]] ** 0.7), reverse=True)

        used = 0
        for chestie in vid_touples:
            # if chestie[2] == 0:
            #     break
            if viz[chestie[0]] > 1:
                continue
            used += videos[chestie[0]]
            if used <= capacity:
                servers[id_server]["videos"][chestie[0]] = vid_data[chestie[0]]
                viz[chestie[0]] += 1
        # for id_video in range(num_vid):
        #     vid_touples.append((id_video, vid_data[id_video]))


max_score = 0
best_conf = {}

def save_sol():
    global best_conf
    best_conf = {}
    for id_server in range(num_server):
        best_conf[id_server] = list(servers[id_server]["videos"])

def load_best():
    for id_server in best_conf:
        servers[id_server]["videos"] = {}
        for id_video in best_conf[id_server]:
            servers[id_server]["videos"][id_video] = {}

def calc_score(stderr):
    global max_score
    total = 0
    nr = 0
    for id_endpoint in range(num_endpoints):
        for id_video in endpoints[id_endpoint]["req"]:
            id_min_server = -1
            lat_min = endpoints[id_endpoint]["latency"]
            for id_server in endpoints[id_endpoint]["servers"]:
                if id_video in servers[id_server]["videos"]:
                    if endpoints[id_endpoint]["servers"][id_server] < lat_min:
                        lat_min = endpoints[id_endpoint]["servers"][id_server]
                        id_min_server = id_server

            lat_video = endpoints[id_endpoint]["latency"]
            nr += endpoints[id_endpoint]["req"][id_video]
            latency_diff = (lat_video - lat_min)
            total += latency_diff * endpoints[id_endpoint]["req"][id_video]
    score = 1000 * total / nr;
    print(score, file=stderr);
    if score > max_score:
        max_score = score
        save_sol()
    else:
        load_best()


retain_number = 10
def redo():
    t1 = time.perf_counter()
    for id_endpoint in range(num_endpoints):
        for id_video in endpoints[id_endpoint]["req"]:
            id_min_server = -1
            lat_min = 99999999
            for id_server in endpoints[id_endpoint]["servers"]:
                if id_video in servers[id_server]["videos"]:
                    if endpoints[id_endpoint]["servers"][id_server] < lat_min:
                        lat_min = endpoints[id_endpoint]["servers"][id_server]
                        id_min_server = id_server
            endpoints[id_endpoint]["attrib"][id_video] = id_min_server
    t2 = time.perf_counter()
    print("vid_data", t2 - t1, file=stderr)

    viz = [0 for j in range(num_vid)]

    global retain_number
    retain_number += 1
    for id_server in range(num_server):
        id_server = randint(0, num_server - 1)
        # print("server", id_server, file=stderr)
        serv = servers[id_server]
        # t1 = time.perf_counter()
        vid_data = [{"count": 0, "reducere": 0} for j in range(num_vid)]
        t2 = time.perf_counter()
        # print("vid_data", t2 - t1, file=stderr)
        iter = 0
        for id_point in serv["endpoints"]:
            endpoint = endpoints[id_point]
            for id_video in endpoint["req"]:
                # iter += 1
                if endpoint["servers"][id_server] > 700:
                    continue
                id_min_server = endpoint["attrib"][id_video]
                req = endpoint["req"][id_video]
                data = vid_data[id_video]
                lat_video = endpoint["latency"]

                if id_min_server == id_server:
                    data["id"] = id_video
                    data["count"] += req
                    latency_diff = (lat_video - endpoint["servers"][id_server])
                    data["reducere"] += latency_diff * req
                    continue

                if id_min_server != -1:
                    lat_video = endpoint["servers"][id_min_server]
                if endpoint["servers"][id_server] > lat_video:
                    continue
                # if id_min_server != -1 and endpoint["servers"][id_min_server] endpoint["servers"][id_min_server]:
                #     continue
                # if id_min_server != -1:
                #     lat_video =
                data["id"] = id_video
                data["count"] += req
                latency_diff = (lat_video - endpoint["servers"][id_server])
                data["reducere"] += latency_diff * req
        t3 = time.perf_counter()
        print("iter", iter, "in", t3 - t2, file=stderr)
        vid_touples = []
        for data in vid_data:
            if data["count"] == 0:
                continue
            vid_touples.append((data["id"], data["count"], data["reducere"]))

        # vid_touples.sort(key=lambda chestie: chestie[2], reverse=True)
        vid_touples.sort(key=lambda chestie: chestie[2] / (videos[chestie[0]] ** 0.6), reverse=True)

        servers[id_server]["videos"] = {}
        used = 0
        for i, chestie in enumerate(vid_touples):
            # if chestie[2] == 0:
            #     break
            # if viz[chestie[0]] > 3:
            #     continue
            # if i > 10 and randint(0, 10) < 2:
            #    continue
            
            # if len(vid_touples) > 4 and i == 0 and randint(0, 4) == 0:
            #     continue
            # if i > max(2, retain_number / 2) and randint(0, 1) == 0:
            #     continue
            used += videos[chestie[0]]
            if used <= capacity:
                servers[id_server]["videos"][chestie[0]] = vid_data[chestie[0]]
                viz[chestie[0]] += 1
        # for id_video in range(num_vid):
        #     vid_touples.append((id_video, vid_data[id_video]))

        # t4 = time.perf_counter()
        # print("gata", t4 - t3, file=stderr)
        if id_server % 50 == 0:
            break


def write_data():
    load_best()
    with open("data.out", "w") as output:
        sys.stdout = output
        print("best", max_score, file=stderr)
        print(num_server)
        for id_server in range(num_server):
            print(id_server, *servers[id_server]["videos"])

def load_data():
    for i in range(num_server):
        servers[i]["videos"] = {}
    with open("kittens-826.out", "r") as input:
        nr = int(input.readline())
        for _ in range(nr):
            data = list(map(int, input.readline().split()))
            id_server = data[0]
            for id_video in data[1:]:
                servers[id_server]["videos"][id_video] = {}
            

def main():
    with open("data.in", "r") as input:
        tmp = sys.stdout
        read_data(input)
        # initialize()
        load_data()
        for i in range(1500):
            redo()
            calc_score(tmp)
            if i % 20 == 0:
                global retain_number
                retain_number = 10
            write_data()
        sys.stdout = tmp


if __name__ == "__main__":
    main()
