from pyvis.network import Network
import json
import webbrowser
import os

def rideshare_network():
    ride_net = Network(cdn_resources='in_line', directed = True, height = '100vh', 
                       width = '100%', select_menu=True)

    with open('./rideshare_community_areas.json') as f:
        ride_data = json.load(f)
        
        nodes = {}

        for ride in ride_data:
            node = ride['pickup_name']
            if node not in nodes:
                nodes[node] = {}
            nodes[node]['total_trips'] = nodes[node].get('total_trips', 0) + int(ride['trips'])
            nodes[node]['lat'] = ride['pickup_lat']
            nodes[node]['lon'] = ride['pickup_lon']
       
        for node in nodes:
            ride_net.add_node(node, 
                              value = nodes[node]['total_trips']*100,
                              x = nodes[node]['lon'] * 10000,
                              y = -nodes[node]['lat'] * 10000,
                              title = f"{node} Total Trips: {nodes[node]['total_trips']}")

        edges = [[ride['pickup_name'], ride['dropoff_name']] for ride in ride_data]

        ride_net.add_edges(edges)

    ride_net.toggle_physics(False)
    # ride_net.show_buttons()
    file_path = os.path.abspath("rideshare.html")
    ride_net.write_html(file_path)

    webbrowser.open("file://" + file_path)

    #print(ride_net.show("rideshare.html"))