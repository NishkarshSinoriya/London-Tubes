from tkinter import *
from tkinter import messagebox
import csv
import matplotlib.pyplot as plt

connections_list = []
stations_list = []
line_list = []
merged_list = []
empty_list = []
tuple_list = []


# function to covert csv files into key value pairs
def csv_reader(csv_file_name, _list):
    with open(csv_file_name) as a:
        _rows = csv.DictReader(a)
        for _row in _rows:
            _list.append(_row)


csv_reader("londonconnections.csv", connections_list)  # List containing dictionaries from london connections csv file.
csv_reader("londonstations.csv", stations_list)  # List containing dictionaries from london stations csv file.
csv_reader("londonlines.csv", line_list)  # List containing dictionaries from london lines csv file.

# Dictionary of all the rows of london lines csv file stored with line_id as key
lines = {}
for i in line_list:
    lines[int(i['line_id'])] = i

# Creating list by merging above 2 lists where value of station1 is equal to id in london stations csv.
for i in connections_list:
    for j in stations_list:
        if i['station1'] == j['id']:
            merged_dict = i | j
            merged_list.append(merged_dict)


def int_conversion(row, field):
    a = row[field]
    row[field] = int(a)


def float_conversion(row, field):
    a = row[field]
    row[field] = float(a)


# Type casting fields in merged list into desired data type
for i in merged_list:
    int_conversion(i, 'station1')
    int_conversion(i, 'station2')
    int_conversion(i, 'line_id')
    int_conversion(i, 'time')
    int_conversion(i, 'id')
    int_conversion(i, 'total_lines')
    float_conversion(i, 'latitude')
    float_conversion(i, 'longitude')

# Introducing a desired id field named edge_id for targeting every dictionary appended in merged list
for i in range(len(merged_list)):
    merged_list[i]['edge_id'] = i

# Creating a List of tuples containing unique pairs of values of station1, station2 and line_id
for i in merged_list:
    empty_list.append((i['station1'], i['line_id']))
    empty_list.append((i['station2'], i['line_id']))

tuple_list = list(set(empty_list))


# Blueprint for Nodes in the metro network
class Nodes:
    def __init__(self, node_id, name, station_id, latitude, longitude):
        self.id = node_id
        self.name = name
        self.station_id = station_id
        self.latitude = latitude
        self.longitude = longitude
        self.neighbour_nodes = []
        self.edges = []
        self.time_log = False


# Blueprint for Edges in the metro network
class Edges:
    def __init__(self, edge_id, start_station, end_station, time, line_id):
        self.edge_id = edge_id
        self.start_station = start_station
        self.end_station = end_station
        self.time = time
        self.line_id = line_id
        self.coordinates = None


# Blueprint for Graph in the metro network
class Graph:
    def __init__(self):
        self.dict_nodes = dict_nodes
        self.dict_edges = dict_edges

    def get_nodes(self, group_id):
        return self.dict_nodes[group_id]

    @staticmethod
    def checkInputs(station_name):
        for a in stations_list:
            if a['name'].lower() == station_name.lower():
                return 1
        return 0

    @staticmethod
    def getId(station_name):
        for z in stations_list:
            if z['name'].lower() == station_name.lower():
                return z['id']

    def getConnectionBetween(self, present_station, next_station):
        if present_station.station_id in next_station.neighbour_nodes:
            for ps in present_station.edges:
                c = self.dict_edges[ps]
                if next_station.station_id in [c.end_station, c.start_station] and present_station.station_id in [
                    c.end_station, c.start_station]:
                    return c
        else:
            return "These two stations are not directly connected"

    def getCoordinates(self, edge, from_id):  # type Graph, type Connection, tuple representing station.station_id
        s1 = self.get_nodes(edge.start_station)  # type Station
        s2 = self.get_nodes(edge.end_station)  # type Station
        if from_id == s1.station_id:
            edge.coordinates = {'lat_from': s1.latitude, 'long_from': s1.longitude, 'lat_to': s2.latitude,
                                'long_to': s2.longitude}
        if from_id == s2.station_id:
            edge.coordinates = {'lat_from': s2.latitude, 'long_from': s2.longitude, 'lat_to': s1.latitude,
                                'long_to': s1.longitude}
        return edge.coordinates

    # function to implement Dijkstra's algorithm
    def djs(self, start_station, end_station):
        try:
            if Graph.checkInputs(start_station):
                start_station_id = Graph.getId(start_station)
                for i in self.dict_nodes:
                    if i[0] == int(start_station_id):
                        start_station = self.dict_nodes[i]
                        break
            else:
                message = 'Invalid start station'
                messagebox.showinfo("showinfo", message)
                return message

            if Graph.checkInputs(end_station):
                end_station_id = Graph.getId(end_station)
                for i in self.dict_nodes:
                    if i[0] == int(end_station_id):
                        end_station = self.dict_nodes[i]
                        break
            else:
                message = 'Invalid end station'
                messagebox.showinfo("showinfo", message)
                return message

            unexplored_stations = dict([(station_hub_id, 1000) for (station_hub_id, time) in self.dict_nodes.items()])
            unexplored_stations[start_station.station_id] = 0  # (198, 11)
            time_log = []
            current_station = start_station
            paths = {
                current_station.station_id: [{'name': current_station.name, 'station_id': current_station.station_id}]}

            while not end_station.time_log:
                for id in current_station.neighbour_nodes:
                    n = self.get_nodes(id)
                    connection_to_neighbour = self.getConnectionBetween(current_station, n)

                    # store the quickest path to each visited station in a dict called Routes:
                    if n.station_id in unexplored_stations:
                        if unexplored_stations[n.station_id] > (
                                unexplored_stations[current_station.station_id] + connection_to_neighbour.time):
                            unexplored_stations[n.station_id] = unexplored_stations[
                                                                    current_station.station_id] + \
                                                                connection_to_neighbour.time
                            paths[n.station_id] = paths[current_station.station_id][:]
                            paths[n.station_id].append(
                                {"name": n.name, 'station_id': n.station_id})

                    # make sure visited stations will not be visited again. Close the loop by changing Current:
                current_station.time_log = True
                time_log.append(unexplored_stations.pop(current_station.station_id))
                for station_id, overall_time in unexplored_stations.items():
                    if overall_time == min(unexplored_stations.values()):
                        next_station = station_id
                current_station = self.get_nodes(next_station)

            # function to draw the route between entered departure and destination stations
            def draw_graph(path):
                try:
                    coordinates_limits = dict(
                        zip(['min_lat', 'max_lat', 'min_long', 'max_long'], [1000, -1000, 1000, -1000]))
                    latest_line_colour = None

                    get_line_colour = lambda line_id: '#999999' if line_id is None else str(
                        '#' + lines[line_id]['colour'])
                    getlinename = lambda line_id: None if line_id is None else str(lines[line_id]['name'])
                    ax = plt.subplot()
                    for r in range(1,
                                   len(path)):  # loop through a list of dictionaries, one for each station on the
                        # selected route
                        start_station = self.get_nodes(path[r - 1]['station_id'])
                        end_station = self.get_nodes(path[r]['station_id'])
                        edge = self.getConnectionBetween(start_station, end_station)
                        self.getCoordinates(edge, start_station.station_id)

                        if True:
                            if float(edge.coordinates['lat_from']) > float(coordinates_limits['max_lat']):
                                coordinates_limits['max_lat'] = edge.coordinates['lat_from']
                            if float(edge.coordinates['lat_from']) < float(coordinates_limits['min_lat']):
                                coordinates_limits['min_lat'] = edge.coordinates['lat_from']
                            if float(edge.coordinates['long_from']) > float(coordinates_limits['max_long']):
                                coordinates_limits['max_long'] = edge.coordinates['long_from']
                            if float(edge.coordinates['long_from']) < float(coordinates_limits['min_long']):
                                coordinates_limits['min_long'] = edge.coordinates['long_from']
                            if float(edge.coordinates['lat_to']) > float(coordinates_limits['max_lat']):
                                coordinates_limits['max_lat'] = edge.coordinates['lat_to']
                            if float(edge.coordinates['lat_to']) < float(coordinates_limits['min_lat']):
                                coordinates_limits['min_lat'] = edge.coordinates['lat_to']
                            if float(edge.coordinates['long_to']) > float(coordinates_limits['max_long']):
                                coordinates_limits['max_long'] = edge.coordinates['long_to']
                            if float(edge.coordinates['long_to']) < float(coordinates_limits['min_long']):
                                coordinates_limits['min_long'] = edge.coordinates['long_to']

                        line_colour = get_line_colour(edge.line_id)
                        if line_colour == latest_line_colour:
                            line_name = None
                        else:
                            line_name = getlinename(edge.line_id)
                        latest_line_colour = line_colour
                        plt.plot([edge.coordinates['long_from'], edge.coordinates['long_to']],
                                 [edge.coordinates['lat_from'], edge.coordinates['lat_to']], marker='o',
                                 linestyle='--',
                                 color=line_colour, label=line_name)

                        ax.annotate(start_station.name,
                                    xy=(edge.coordinates['long_from'], edge.coordinates['lat_from']),
                                    xytext=(
                                        float(edge.coordinates['long_from']) + 0.002,
                                        float(edge.coordinates['lat_from']) - 0.002))

                        ax.annotate(end_station.name,
                                    xy=(edge.coordinates['long_to'], edge.coordinates['lat_to']),
                                    xytext=(
                                        float(edge.coordinates['long_to']) + 0.002,
                                        float(edge.coordinates['lat_to']) - 0.002))

                    ax.set_xticks(
                        [-0.60, -0.55, -0.50, -0.45, -0.40, -0.35, -0.30, -0.25, -0.20, -0.15, -0.10, -0.05, 0, 0.05,
                         0.10,
                         0.15, 0.20])

                    ax.set_yticks([51.40, 51.45, 51.50, 51.55, 51.60, 51.65, 51.70])
                    ax.set_xlim((float(coordinates_limits['min_long']) - 0.02),
                                (float(coordinates_limits['max_long']) + 0.02))
                    ax.set_ylim((float(coordinates_limits['min_lat']) - 0.02),
                                (float(coordinates_limits['max_lat']) + 0.02))
                    plt.xlabel('Longitude')
                    plt.ylabel('Latitude')
                    plt.legend()
                    plt.show()

                except EXCEPTION:
                    pass

            messagebox.showinfo("showinfo",
                                f"Travelling from {start_station.name} to {end_station.name} will take {time_log[-1]} minutes.")

            a = messagebox.askyesno("askyesno", "do you want to see the route?")
            if a:
                draw_graph(path=paths[end_station.station_id])
            else:
                root.destroy()

        except EXCEPTION:
            messagebox.showerror("showerror", "To view the route with valid inputs")


dict_nodes = {}
dict_edges = {}


# Function to help in making Nodes for tuples containing station2 since it was not used as dictionary merging criteria.
def assist(tuple_id, attribute):
    for ij in stations_list:
        if int(ij['id']) == tuple_id:
            return ij[attribute]


# Making Nodes where values in tuples of tuple list is equal to value in dictionaries of merged list.
for i in tuple_list:
    temp = {}
    temp1 = {}
    for j in merged_list:
        if i[0] == j['station1'] and i[1] == j['line_id']:
            temp[i] = Nodes(j['station1'], j['name'], i, float(j['latitude']), float(j['longitude']))
            dict_nodes = dict_nodes | temp
        if i[0] == j['station2'] and i[1] == j['line_id']:
            temp1[i] = Nodes(j['station2'], assist(j['station2'], 'name'), i, float(assist(j['station2'], 'latitude')),
                             float(assist(j['station2'], 'longitude')))
            dict_nodes = dict_nodes | temp1

# Making Edges consisting of unique tuple pairs to make sure they are unique.
for i in merged_list:
    temp = {
        i['edge_id']: Edges(i['edge_id'], tuple([i['station1'], i['line_id']]), tuple([i['station2'], i['line_id']]),
                            i['time'], i['line_id'])}
    dict_edges = dict_edges | temp

# Joining Nodes and Edges using objects and updating n nodes within Nodes.
for i in range(len(merged_list)):
    var1 = dict_nodes[tuple([merged_list[i]['station1'], merged_list[i]['line_id']])]
    var2 = dict_nodes[tuple([merged_list[i]['station2'], merged_list[i]['line_id']])]
    var1.edges.append(i)
    var2.edges.append(i)
    var1.neighbour_nodes.append(tuple([merged_list[i]['station2'], merged_list[i]['line_id']]))
    var2.neighbour_nodes.append(tuple([merged_list[i]['station1'], merged_list[i]['line_id']]))

keys = range(1, len(stations_list) + 2)
values = [[] for i in keys]
groups = dict(zip(keys, values))

for id_tuple, node in dict_nodes.items():
    groups[id_tuple[0]].append(id_tuple)
i = 1500
roaming_time = 0  # Considering that it takes zero time for the passenger to change the stations
for hub in groups.values():
    for node in hub:
        for s in hub:
            if node != s:
                dict_nodes[node].neighbour_nodes.append(s)
                dict_nodes[node].edges.append(i)
                dict_edges[i] = Edges(i, node, s, roaming_time, None)
                i += 1

# GUI of the application

root = Tk()
root.geometry("600x400")
root.title("London Transport Underground Network")
root.maxsize(500, 120)
root.minsize(500, 120)


def func():
    Graph().djs(departure_var.get(), destination_var.get())


Label(root, text="Welcome to the London Transport", bg="olive", relief=GROOVE).grid(row=0, column=1)
Label(root, text="-------------------------------------", fg="olive").grid(row=1, column=1)
Label(root, text="Departure Station", fg="white").grid(row=2, column=0)
Label(root, text="Destination Station", fg="white").grid(row=3, column=0)
departure_var = StringVar()
destination_var = StringVar()
Entry(root, textvariable=departure_var, bg="white", fg="black").grid(row=2, column=1)
Entry(root, textvariable=destination_var, bg="white", fg="black").grid(row=3, column=1)
Button(root, text="Search", padx=20, fg="black", command=func).grid(row=3, column=2)
root.mainloop()
