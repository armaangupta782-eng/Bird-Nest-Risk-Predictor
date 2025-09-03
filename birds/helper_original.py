import streamlit as st
import folium
from folium import plugins
from streamlit_folium import  folium_static
import pandas as pd
import base64
import pydeck as pdk



images = ['bird_images\\Little Grebe.jpg','bird_images\\Little Ringed Plover.jpg','bird_images\\Ashy Drongo.webp', 'bird_images\\Asian Brown Flycatcher.webp', 'bird_images\\Asian Koel.jpg', 'bird_images\\Barn Swallow.webp', 'bird_images\\Black Drongo.webp', 'bird_images\\Black Kite.jpg', 'bird_images\\Black-crowned Night-Heron.webp', 'bird_images\\Black-hooded Oriole.webp', 'bird_images\\Black-naped Monarch.webp', 'bird_images\\Black-winged Kite.jpg', 'bird_images\\Black-winged Stilt.webp', "bird_images\\Blyth's Reed Warbler.webp", 'bird_images\\Bronzed Drongo.webp', 'bird_images\\Brown Boobook.webp', 'bird_images\\Brown Shrike.webp', 'bird_images\\Cattle Egret.webp', 'bird_images\\Common Greenshank.webp', 'bird_images\\Common Iora.webp', 'bird_images\\Common Kingfisher.webp', 'bird_images\\Common Myna.webp', 'bird_images\\Common Rosefinch.webp', 'bird_images\\Common Sandpiper.webp', 'bird_images\\Common Tailorbird.webp', 'bird_images\\Coppersmith Barbet.webp', 'bird_images\\Crested Serpent-Eagle.jpg', 'bird_images\\Crested Serpent-Eagle.webp', 'bird_images\\Eurasian Collared-Dove.webp', 'bird_images\\Eurasian Coot.webp', 'bird_images\\Eurasian Hoopoe.webp', 'bird_images\\Eurasian Marsh-Harrier.webp', 'bird_images\\Eurasian Moorhen.webp', 'bird_images\\Garganey.webp', 'bird_images\\Glossy Ibis.webp', 'bird_images\\Gray Heron.webp', 'bird_images\\Gray Wagtail.webp', 'bird_images\\Gray-breasted Prinia.webp', 'bird_images\\Gray-headed Canary-Flycatcher.webp', 'bird_images\\Great Egret.jpg', 'bird_images\\Greater Coucal.webp', 'bird_images\\Greater Racket-tailed Drongo.webp', 'bird_images\\Green Sandpiper.webp', 'bird_images\\Green Warbler.webp', 'bird_images\\Greenish Warbler.webp', 'bird_images\\House Crow.webp', 'bird_images\\House Sparrow.webp', 'bird_images\\Kentish Plover.webp', 'bird_images\\Large-billed Crow.webp', 'bird_images\\Laughing Dove.webp', 'bird_images\\Little Egret.webp', 'bird_images\\Pied Kingfisher.webp', 'bird_images\\Plain Prinia.webp', 'bird_images\\Puff-throated Babbler.webp', 'bird_images\\Purple Heron.webp', 'bird_images\\Purple Sunbird.webp', 'bird_images\\Red-rumped Swallow.jpg', 'bird_images\\Red-wattled Lapwing.webp', 'bird_images\\Red-whiskered Bulbul.webp', 'bird_images\\Rock Pigeon.webp', 'bird_images\\Rose-ringed Parakeet.webp', 'bird_images\\Rufous Treepie.webp', 'bird_images\\Scaly-breasted Munia.webp', 'bird_images\\Spotted Dove.webp', 'bird_images\\Stork-billed Kingfisher.webp', "bird_images\\Tickell's Blue Flycatcher.webp", 'bird_images\\Western Yellow Wagtail.webp', 'bird_images\\Whiskered Tern.webp', 'bird_images\\White-breasted Waterhen.webp', 'bird_images\\White-throated Kingfisher.webp', 'bird_images\\Wood Sandpiper.webp', 'bird_images\\Zitting Cisticola.webp']
images = [image.replace('\\', '/') for image in images]


def get_image(name):
    for path in images:
        if name in path:
            return  path

def scientific_n(name,df):
    d= df[df['common_name']==name]
    d.reset_index(drop=True,inplace=True)
    v= d.scientific_name[0]
    return v

# Scatterplot Layer
def map_3d(name , df):
    data = df[df['common_name'] == name]
    scatterplot_layer = pdk.Layer(
        'ScatterplotLayer',
        data,
        get_position='[longitude, latitude]',
        get_radius=50000,
        get_color='[rating * 75, 150, 0]',
        pickable=True,
        auto_highlight=True
    )

    # Set the viewport location and zoom level
    view_state = pdk.ViewState(
        latitude=data['latitude'].mean(),
        longitude=data['longitude'].mean(),
        zoom=3,
        pitch=50
    )

    # Create Deck object
    deck = pdk.Deck(
        layers=[scatterplot_layer],
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/satellite-streets-v11',
        tooltip={"html": "<b>Common Name:</b> {common_name}<br><b>Scientific Name:</b> {scientific_name}<br><b>Rating:</b> {rating}"}
    )

    return deck



#@st.cache
def get_info_bird(name):
    bird_d = {
    "Ashy Drongo": "A slim and agile bird, the Ashy Drongo is known for its distinctive ash-grey plumage and forked tail. It is often seen perched prominently, catching insects in mid-air. Common across Asia, it is known for its mimicking abilities and territorial behavior.",
    "Asian Brown Flycatcher": "This small, unobtrusive flycatcher features plain brown upper parts and white underparts. It breeds across Asia and migrates to Southeast Asia in winter. Its diet mainly consists of insects, which it catches in flight with sharp acrobatics.",
    "Asian Koel": "A member of the cuckoo order, the Asian Koel is famous for its loud, repeating koo-Ooo call. It is a brood parasite, laying its eggs in the nests of crows and other hosts. Males are glossy black with a striking red eye, whereas females sport spotted brown plumage.",
    "Barn Swallow": "Easily identified by its deeply forked tail and agile flight, the Barn Swallow is found across the world. It feeds primarily on insects caught in flight. Known for building cup-shaped mud nests near human habitation.",
    "Black Drongo": "The Black Drongo is easily recognizable by its glossy black feathers and forked tail. It is a fearless bird, known to dive at larger predators to protect its territory. Widely found across Asia, it feeds on insects and is known for its aggressive nature.",
    "Black Kite": "A medium-sized raptor with a slightly forked tail, the Black Kite is a common sight in both urban and rural areas. It is highly adaptable, feeding on a variety of diets including small mammals, birds, and even garbage.",
    "Black-crowned Night-Heron": "This stocky heron has a black crown and back, with contrasting pale underparts. Known for its nocturnal habits, it is often seen at dusk flying with slow wingbeats. It feeds mainly on fish, amphibians, and small mammals.",
    "Black-hooded Oriole": "With its striking black and bright yellow plumage, the Black-hooded Oriole is a visual treat. It inhabits forests and wooded areas, feeding on insects, fruits, and nectar. Its melodious calls are a common sound in its habitat.",
    "Black-naped Monarch": "This striking bird features a distinctive black nape and crest on a blue body. It is primarily insectivorous and prefers dense forests. Known for its beautiful, fluty call, it is also noted for its hanging nests.",
    "Black-winged Kite": "A small kite with piercing red eyes and predominantly grey and white plumage. It hovers like a kestrel when hunting small rodents and insects. Found in open grasslands and fields, it is a solitary bird except during breeding season.",
    "Black-winged Stilt": "Characterized by its extremely long pink legs and sleek black-and-white body, the Black-winged Stilt inhabits wetlands across the globe. It feeds on insects and aquatic invertebrates, often seen foraging in shallow waters.",
    "Blyth's Reed Warbler": "A small, inconspicuous warbler that breeds in Asia and winters in the Indian subcontinent. It has a brownish appearance and a distinct supercilium. The bird is known for its varied and melodious song.",
    "Bronzed Drongo": "The Bronzed Drongo stands out with its metallic bronze-colored body and deeply forked tail. It is found in forests across South and Southeast Asia, feeding on insects and often seen in mixed-species flocks.",
    "Brown Boobook": "Also known as the Brown Hawk-owl, this bird of prey has a rounded head and is known for its distinctive call that sounds like a repeated 'whoop'. It hunts at night, feeding on small mammals and insects.",
    "Brown Shrike": "A small, robust shrike with a distinctive brown back and a white throat. It impales its prey on thorns or barbed wire, which is typical behavior for shrikes. It breeds in East Asia and migrates to South Asia in winter.",
    "Cattle Egret": "Originally native to Africa and Asia, this small heron has successfully spread worldwide. It is often seen in fields among cattle, feeding on insects disturbed by the livestock. Its breeding plumage includes buff-colored feathers on head and back.",
    "Common Greenshank": "This long-legged wader is recognized by its grey-brown plumage and slightly upturned bill. It is commonly found in wetlands and coastal areas, feeding on a variety of aquatic animals. It is a migrant, breeding in northern parts of Europe and Asia.",
    "Common Iora": "A small, vividly-colored bird, the Common Iora has a yellow and green plumage that is especially bright during the breeding season. It is very active and vocal, feeding on insects in the foliage of trees and bushes.",
    "Common Kingfisher": "Known for its brilliant blue and orange plumage, the Common Kingfisher is found near rivers and lakes where it dives to catch fish. Its rapid flight and distinctive fishing technique make it a fascinating bird to observe.",
    "Common Myna": "Highly adaptable and known for its boldness, the Common Myna thrives in urban environments. It has a brown body, black head, and yellow patches behind the eyes. Often seen in groups, it feeds on insects, fruits, and discarded human food.",
    "Common Rosefinch": "This finch is mostly found in the northern hemisphere, sporting a bright red face and breast in males during the breeding season. It primarily feeds on seeds, but also consumes insects during the summer.",
    "Common Sandpiper": "A small wader with a distinctive 'bobbing' motion when it walks along the water's edge. It has a brown upper body and white underparts, feeding on insects and small invertebrates found in the mud.",
    "Common Tailorbird": "Famous for its nest made of leaves 'sewn' together, the Common Tailorbird is a small, brightly colored bird, with a long, upward-pointing tail, often seen in gardens and wooded areas. It feeds on insects and sings a loud, cheerful song.",
    "Coppersmith Barbet": "Named for its metronomic call that sounds like a coppersmith at work, this small green bird with a red forehead is often seen in gardens and wooded areas. It feeds on fruits and insects and is known for its distinctive drumming sound.",
    "Crested Serpent-Eagle": "A medium-sized bird of prey known for its distinctive crest and habit of soaring on thermals. Found in forested habitats, it primarily feeds on snakes and other reptiles.",
    "Eurasian Collared-Dove": "This pale, long-tailed dove is known for its distinctive black neck collar. Originally from Asia, it has expanded its range dramatically across Europe and North America. It feeds on seeds and grains and is often seen in open country near human habitation.",
    "Eurasian Coot": "A water bird with a distinctive white beak and forehead shield, the Eurasian Coot is often seen in open water bodies. Despite its swimming habits, it has lobed, not webbed, feet. It is aggressive and territorial during the breeding season.",
    "Eurasian Hoopoe": "With its striking black and white wings, long black bill, and distinctive crest, the Eurasian Hoopoe is found across Afro-Eurasia. It feeds primarily on insects, probing the ground with its bill. Its unique 'oop-oop-oop' call is unmistakable.",
    "Eurasian Marsh-Harrier": "This bird of prey is known for its low, quartering flight over marshes and reed beds. It has a brown plumage with a distinctive creamy head in males. It preys on small birds and mammals, and occasionally on insects and reptiles.",
    "Eurasian Moorhen": "A common waterbird with a black body and red and yellow beak, the Eurasian Moorhen is often seen swimming in ponds or walking near water edges. It is adaptable and feeds on both plants and small aquatic creatures.",
    "Garganey": "A small dabbling duck, the Garganey has a distinctive white stripe over its eye. It migrates from Europe to Africa and southern Asia in winter. Feeds on aquatic vegetation, insects, and small fish.",
    "Glossy Ibis": "This wading bird has a distinctive glossy, iridescent plumage and a long, curved bill. It is found in wetlands where it probes the mud for food such as small fish, insects, and crustaceans.",
    "Gray Heron": "A large wader known for its long neck and legs, the Gray Heron is found across temperate Europe and Asia. It stands still at water's edge to ambush prey, mainly fish and amphibians.",
    "Gray Wagtail": "The Gray Wagtail is notable for its long tail and distinctive bobbing movement. Its upperparts are grey and the underparts are light with yellow. It is commonly found near fast-flowing waters where it feeds on insects and small invertebrates.",
    "Gray-breasted Prinia": "This small bird is common in grasslands and open woodland. It has a grey breast, a long tail, and is known for its loud, repetitive song. The diet consists mostly of insects.",
    "Gray-headed Canary-Flycatcher": "Small and sprightly, this bird has a grey head and greenish body. It catches insects in mid-air with quick, darting flights. Found in forests and woodlands across Asia.",
    "Great Egret": "Much larger than most other egrets, this bird is all white with a long neck and sharp yellow bill. It is widely distributed, seen in wetlands hunting for fish and amphibians. Known for its spectacular breeding plumage.",
    "Greater Coucal": "A large non-parasitic member of the cuckoo order, the Greater Coucal is black with a distinctive coppery back. It has deep, booming calls and is often seen in open forests and grasslands. Feeds on insects, small vertebrates, and eggs.",
    "Greater Racket-tailed Drongo": "This bird is known for its remarkable tail feathers with disk-like ends. It is glossy black with a blue sheen and is a fearless species, known to mimic the calls of other birds. Found in dense forests.",
    "Green Sandpiper": "A small wader that frequents muddy and vegetated marshlands. It has a distinctive white rump and a dark upper body, feeding on insects and small invertebrates found in the water.",
    "Green Warbler": "A small leaf-warbler that migrates from Europe to Africa and southern Asia in the winter. It has a greenish body and feeds on insects. Known for its sweet song, it breeds in forests and woodlands.",
    "Greenish Warbler": "Another small leaf-warbler, this bird is similar in habits to the Green Warbler but with a more greenish tint and a distinct vocalization. It breeds in temperate Eurasia and winters in tropical Asia.",
    "House Crow": "Highly intelligent and adaptable, the House Crow is grey and black and thrives in urban areas. It feeds on a wide range of food from waste to small animals. It is often seen in large, noisy groups.",
    "House Sparrow": "Once very common, the House Sparrow is a small bird with a stout body, native to Europe and Asia but now found worldwide. It feeds primarily on seeds and scraps and nests almost exclusively near humans.",
    "Kentish Plover": "A small wader found on sandy beaches and salt flats, the Kentish Plover has a white and brown plumage. It is known for its quick movements and feeds on insects and small crustaceans.",
    "Large-billed Crow": "Similar to the House Crow but larger, with a more robust bill. It is also highly adaptable and intelligent, found in forested and urban areas across Asia. It has a varied diet that includes insects, waste, and small animals.",
    "Laughing Dove": "Smaller than the Common Pigeon, the Laughing Dove has a pinkish body and a distinctive blue-grey head with a black collar. It has a gentle, cooing call and is found in arid areas near human settlements.",
    "Little Egret": "A small, agile egret with snowy white plumage and black legs and bill. It hunts in shallow water for fish and amphibians. Known for its delicate movements and sometimes seen with cattle.",
    "Little Grebe": "Also known as the Dabchick, this small waterbird is excellent at diving and swimming. It has a dark brown body and a distinctive whistling call. Found in ponds and lakes, feeding on fish and aquatic insects.",
    "Little Ringed Plover": "A small plover with a distinctive white ring around its neck and a brown back. It breeds in gravel and sand along riverbanks and lakeshores, feeding on insects and worms.",
    "Little Spiderhunter": "This small bird has a long curved beak, perfect for feeding on nectar. It has a greenish body and is often seen hanging from flower clusters. Found in forests and gardens.",
    "Pied Kingfisher": "Identifiable by its black and white plumage and crest, the Pied Kingfisher is one of the few kingfishers that hover over water to hunt fish. It is commonly seen by lakes and rivers.",
    "Plain Prinia": "A small, drab-colored warbler commonly found in grasslands and scrubby areas. It feeds on insects and builds a ball-shaped nest in a bush. It has a loud and distinctive call.",
    "Puff-throated Babbler": "This babbler has a distinctive white throat that puffs out during calls. It is brown above and whitish below, found in thick undergrowth where it feeds on insects.",
    "Purple Heron": "Taller and slimmer than the Gray Heron, the Purple Heron has a long neck and a striking purple-grey plumage. It is secretive and more solitary, found in dense reed beds where it hunts for fish.",
    "Purple Sunbird": "A small and vividly colored sunbird, males are iridescent purple while females are olive above and yellowish below. They feed largely on nectar but also eat insects and spiders.",
    "Red-rumped Swallow": "Similar in appearance to the Barn Swallow but with a distinctive red rump. It builds its mud nests almost exclusively on human-made structures. It feeds on insects caught in flight.",
    "Red-wattled Lapwing": "Easily recognizable by its loud calls and bold pattern of black, white, and red, the Red-wattled Lapwing is found in open landscapes across South and Southeast Asia. It feeds on insects and other small invertebrates.",
    "Red-whiskered Bulbul": "This bulbul is easily identified by the red patch under its eye and a crested head. It is a common resident in tropical Asia, found in gardens and forests. It feeds on fruits and small insects.",
    "Rock Pigeon": "Known for its ability to adapt to urban environments, the Rock Pigeon has a varied diet and can live almost anywhere. It has a grey body and is often seen in flocks in city squares and parks.",
    "Rose-ringed Parakeet": "A popular pet, the Rose-ringed Parakeet is bright green with a distinctive red or black neck ring on males. It is noisy and gregarious and has adapted well to urban environments, feeding on fruits and nuts.",
    "Rufous Treepie": "A member of the crow family, the Rufous Treepie is distinctive with its rufous body and long tail. It is very vocal and feeds on insects and fruits. Commonly seen in open forests across Asia.",
    "Scaly-breasted Munia": "This small finch is known for its distinctive scale-like feather markings on the breast and belly. It feeds on grass seeds and is often seen in flocks in grasslands and cultivated fields.",
    "Spotted Dove": "Similar in size to the Laughing Dove, the Spotted Dove has a distinctive black and white spotted necklace. It is quiet and unobtrusive, found in open woods and gardens where it feeds on seeds.",
    "Stork-billed Kingfisher": "One of the largest kingfishers, the Stork-billed Kingfisher has a huge bill and a colorful plumage of blue and brown. It is found near rivers and lakes where it hunts fish from a perch.",
    "Tickell's Blue Flycatcher": "A small, beautiful flycatcher with bright blue upperparts and orange breast. It is found in thick undergrowth and dense scrub. It feeds on insects, often caught by flycatching.",
    "Western Yellow Wagtail": "A small bird with a long tail and distinctive walk, the Western Yellow Wagtail is brightly colored during the breeding season. It feeds on insects from the ground and is often seen in wet meadows.",
    "Whiskered Tern": "A waterbird with a graceful flight, the Whiskered Tern has a black head and grey body in breeding plumage. It dives to catch fish and is often seen in coastal areas and inland water bodies.",
    "White-breasted Waterhen": "A common waterbird with a loud and distinctive call, the White-breasted Waterhen has a striking contrast of black and white colors. It skulks in the marshes and is shy and elusive.",
    "White-throated Kingfisher": "Also known as the White-breasted Kingfisher, this species is more often seen away from water bodies. It has a vivid blue back and a white throat and breast, feeding on fish, frogs, and large insects.",
    "Wood Sandpiper": "This small wader is known for its slender appearance and nervous movements. It has a brown back and white underparts, and feeds on insects and small invertebrates found in muddy marshlands.",
    "Zitting Cisticola": "A small, inconspicuous bird known for its 'zitting' call that resembles a series of clicks. Found in grassy fields and open areas, it is brown with a heavily streaked back. It builds a unique ball-like nest in tall grass."
}

    return bird_d[name]




def svg_to_dataurl(path_to_svg):
    with open(path_to_svg, 'r') as f:
        svg = f.read()
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode('utf-8')).decode('utf-8')

url=svg_to_dataurl('/Users/mayanksingh/Desktop/All desktop/Desktop 19 Aug 2025/chatgpt/Nest_project/birds/crow-solid.svg')

# Load data
#df = pd.read_csv

def heatmap_bird(name ,df ):
    bird_data = df[df['common_name']==name]

    # Load data
    #df = pd.read_csv('path_to_your_file.csv')
    bird_icon_url=url
    # Create a map
    map = folium.Map(location=[  bird_data ['latitude'].mean(),   bird_data['longitude'].mean()], zoom_start=5)


    # Create marker cluster
    marker_cluster = plugins.MarkerCluster().add_to(map)
    for index, row in bird_data.iterrows():
        icon = folium.CustomIcon(
            icon_image=bird_icon_url,
            icon_size=(30, 30)  # Size of the icon in pixels
        )
        folium.Marker(
            location=[row['latitude'], row['longitude']],icon=icon,
            popup=f"Common Name: {row['common_name']}<br>Species: {row['primary_label']}"
        ).add_to(marker_cluster)

    # Create heatmap
    data =   bird_data[['latitude', 'longitude']].values.tolist()
    heatmap = plugins.HeatMap(data)
    map.add_child(heatmap)

    # Add layer control
    folium.LayerControl().add_to(map)

    # Save or display the map
   # map.save(f'cluster_and_heatmap{name}.html')
    return folium_static(map,width=1200)
"""df = pd.read_csv('train_metadata.csv')
df.dropna(inplace=True)
print(heatmap_bird("Rock Pigeon",df))"""

"""audio_path= r'birdsCLEF\train_audio\asbfly\XC49755.ogg'
audio_file = open(audio_path, 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/ogg', start_time=0)"""

'''def load_audio(name):
    bird_data = df[df['common_name'] == name]
    if bird_data.empty:
        st.error("No data found for the specified bird.")
        return None
    audio_f_path = bird_data.iloc[0]['filepath']
    return audio_f_path

def main():
    st.title("Bird Audio Player")
    bird_name = st.text_input("Enter the bird's common name to play audio:", "")
    if bird_name:
        audio_path = load_audio(bird_name)
        if audio_path:
            audio_file = open(audio_path, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/ogg', start_time=0)'''
