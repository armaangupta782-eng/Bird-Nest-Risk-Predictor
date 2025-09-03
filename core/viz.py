import os
import base64
import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
import pydeck as pdk

BIRDS_DIR = "birds"
IMG_DIR = os.path.join(BIRDS_DIR, "bird_images")
SVG_CROW = os.path.join(BIRDS_DIR, "crow-solid.svg")  # optional icon


BIRD_DESCRIPTIONS = {
    "Ashy Drongo": "A sleek bird with ash-grey plumage and a deeply forked tail, the Ashy Drongo is an agile acrobat in flight. Its sharp, whistling calls are often heard in wooded habitats across Asia. This drongo is known for its mimicking ability, sometimes imitating the calls of other birds and even mammals, which helps it in territorial defense and confusing predators. Typically seen perched high, it swoops down to catch a variety of flying insects.",
    
    "Asian Brown Flycatcher": "A small, understated bird with soft brown upperparts and clean white underparts, the Asian Brown Flycatcher is an expert flycatcher and hunter of insects. It breeds in temperate Asia and migrates to warmer southern areas in winter. Preferring dense shrubs and woodland edges, this bird darts out from a low perch to snatch insects mid-air with swift precision, often flicking its tail up as it balances on thin branches.",
    
    "Asian Koel": "Famed for its loud and melodious ‘koo-ooo’ calls that mark early mornings and evenings, the Asian Koel is a distinctive and widespread member of the cuckoo family. Males display a glossy black plumage while females have spotted brown tones that provide camouflage. This species practices brood parasitism, laying its eggs in the nests of crows and other hosts, relying on them to raise its young. Koels primarily feast on fruits and insects, frequently calling from treetops in urban and rural gardens alike.",
    
    "Barn Swallow": "Recognizable by its deep forked tail and iridescent blue upperparts contrasted with rusty underparts, the Barn Swallow is a masterful insect catcher on the wing. It exhibits strong, graceful flight and migrates widely across continents to breed in open areas close to water and human habitation. These birds are skillful builders, crafting cup-shaped mud nests often on beams and ledges of barns, bridges, and buildings, bonding in tight social groups.",
    
    "Black Drongo": "A strikingly glossy black bird with a forked tail, the Black Drongo is known for its fearless and aggressive nature, often challenging larger birds and even predators to protect its territory. It prefers open habitats like fields, gardens, and forest edges where it hunts a diet rich in flies, beetles, and other flying insects. This drongo is a skillful aerial hunter and uses its loud, metallic calls to warn of approaching threats. It is a familiar and charismatic presence in many parts of Asia.",
    
    "Black Kite": "An adaptable and widespread bird of prey with a slightly forked tail, the Black Kite thrives in urban centers and rural landscapes alike. This opportunistic scavenger feeds on carrion, small mammals, fish, and insects, often soaring gracefully on thermal currents while searching for food. Black Kites are gregarious, sometimes seen in large communal roosts, and are known for their sharp eyesight and agile flight. They play an important role in the ecosystem by cleaning up dead animals.",
    
    "Black-crowned Night-Heron": "A chunky, nocturnal heron identified by its black crown and back contrasting with pale grey wings and body. Active mostly at dusk and night, it hunts quietly in shallow waters for fish, amphibians, crustaceans, and small mammals. This secretive bird often stands motionless for long periods before striking with lightning speed at prey. Black-crowned Night-Herons nest colonially in trees near wetlands and are found across Asia, Africa, and the Americas.",
    
    "Black-hooded Oriole": "Bright and eye-catching, the Black-hooded Oriole sports a striking yellow body with a contrasting black hood covering its head and throat. Preferring open forest and woodland edges, it feeds on insects, fruits, and nectar, moving actively through the canopy. Its melodious and fluty songs contribute to the vibrant forest soundscape. Common across South and Southeast Asia, it often stays in pairs and uses its strong bill to forage among foliage.",
    
    "Black-naped Monarch": "A beautiful and delicate insectivore distinguished by sky-blue plumage and a notable black nape patch that extends to a prominent crest. The Black-naped Monarch prefers dense, moist forests where it gleans insects from leaves and twigs. Known for its melodious calls and hanging nests, this species exhibits territorial behavior during breeding seasons. Its striking coloration makes it a favorite among birdwatchers in tropical Asia.",
    
    "Black-winged Kite": "A small raptor with pale grey and white plumage and piercing red eyes, the Black-winged Kite exhibits swift, hovering flight over open fields and grasslands when hunting small mammals and insects. It typically hunts by quartering low over terrain and rapidly dropping to seize prey. Solitary except during mating seasons, it nests in trees and is known for its graceful hovering similar to kestrels.",
    
    "Black-winged Stilt": "Elegant and unmistakable, the Black-winged Stilt is a wetlands specialist with very long pink legs and a slender black and white body. It probes shallow waters with its long, thin bill, feeding on aquatic insects, small crustaceans, and mollusks. Its high-pitched calls and group behaviors are characteristic in marshes and lakeshores worldwide. These birds nest in colonies, often on bare patches of muddy land.",
    
    "Blyth's Reed Warbler": "A modestly colored, small warbler with brownish upperparts and creamy underparts, Blyth’s Reed Warbler inhabits marshy reed beds and dense vegetation. Its frequent yet varied song helps it establish territories and attract mates during breeding in Asia. It migrates south during winter and primarily feeds on insects gleaned from reeds and shrubs. The bird’s furtive behavior and subtle plumage make it a challenge to spot but rewarding for dedicated watchers.",
    
    "Bronzed Drongo": "The Bronzed Drongo is notable for its metallic bronze sheen covering its black plumage and its deeply forked tail. This bold and intelligent bird forages in mixed-species flocks, often dominating competing insectivores in tropical forests. It is an aerial hunter, catching beetles, flies, and other insects mid-flight with remarkable agility. The Bronzed Drongo also mimics calls of other birds and gives harsh, ringing notes to communicate.",
    
    "Brown Boobook": "Also known as the Brown Hawk-Owl, this nocturnal bird of prey has warm brown plumage and large yellow eyes. It inhabits tropical and subtropical forests where it hunts small mammals, insects, and birds by silently gliding through the night. The species is known for its distinctive repetitive 'whoop' call heard after dusk. It nests in tree cavities and is an important predator controlling rodent populations.",
    
    "Brown Shrike": "A robust and assertive bird, the Brown Shrike exhibits warm brown upperparts contrasted with a white throat and underparts. This species is famous for impaling prey such as insects and small vertebrates on thorns or barbs as a food cache. It breeds in temperate Asia and migrates to tropical South Asia for winter. Brown Shrikes prefer open country with scattered trees and bushes where they perch conspicuously to hunt.",
    
    "Cattle Egret": "Native to Africa and Asia but now globally widespread, the Cattle Egret often follows large grazing mammals, feeding on insects and small animals disturbed by their movement. It is shorter and stockier compared to other egrets with buff-colored breeding plumage adorning the head and back during nest season. Preferring wetlands, fields, and pastures, it nests in colonies often shared with other herons and storks.",
    
    "Common Greenshank": "A tall, long-legged wader with speckled grey-brown plumage and an upturned bill, the Common Greenshank frequents wetlands, estuaries, and coastal lagoons. It feeds on aquatic invertebrates, small fish, and amphibians, often probing soft mud or shallow water. This migratory bird breeds in northern Europe and Asia and winters in tropical coastal regions. Its distinctive loud, ringing calls are commonly heard near its habitats.",
    
    "Common Iora": "A small, brightly colored bird with striking yellow and green plumage, the Common Iora is vivacious and active in forest canopies and gardens. Males build elaborate nests and perform energetic courtship displays. It feeds primarily on insects, gleaning from leaves and branches. Its loud and melodious calls fill the daytime hours in its tropical South and Southeast Asian range.",
    
    "Common Kingfisher": "A jewel-like bird with vivid blue and orange plumage, the Common Kingfisher hunts by diving swiftly from a perch into freshwater streams, rivers, and lakes. It captures small fish and aquatic insects using its sharp bill. Territorial and solitary outside of breeding season, this kingfisher nests in burrows dug into earth banks near water. Its rapid flight and brilliant colors make it a favorite sight for nature lovers.",
    
    "Common Myna": "Recognized by its brown body, black hooded head, and bright yellow wattles, the Common Myna is highly adaptable to urban and rural environments. It exhibits bold and social behavior, feeding on insects, fruits, and food waste. This intelligent omnivore often forms noisy flocks and is known for its complex vocalizations and ability to mimic human sounds. It nests in cavities, including urban buildings.",
    
    "Common Rosefinch": "Known for the male’s vibrant red face and breast during the breeding season, the Common Rosefinch inhabits open woodlands, scrublands, and forest edges across Eurasia. It feeds primarily on seeds, occasionally supplementing its diet with insects in warmer months. This finch is often heard singing a melodic series of whistles and trills from bushes and tree tops. Females and juveniles sport a more subdued brownish coloration.",
    
    "Common Sandpiper": "A small, nimble wader with brown upperparts and white underparts, the Common Sandpiper is frequently seen along the edges of freshwater bodies bobbing its tail up and down as it forages. It feeds mainly on insects, crustaceans, and other invertebrates found in mud or shallow water. Breeding in Europe and Asia, this species migrates to warmer coastal regions for winter. It nests on the ground in open or semi-open areas.",
    
    "Common Tailorbird": "A tiny, lively bird famed for sewing leaves together with plant fibers to create its unique nest. Common Tailorbirds are greenish on top with brighter yellowish underparts and have a long, upright tail. They inhabit gardens, forests, and scrubby areas, feeding on insects and nectar. The bird’s loud, chirpy songs enliven greenery wherever it dwells, and it is common across South and Southeast Asia.",
    
    "Coppersmith Barbet": "Named for its rhythmic, metallic tapping call reminiscent of a coppersmith's hammer, this small barbet has bright green plumage accented with red and yellow patches on the head and throat. It is often found in orchards, gardens, and open forests feeding on fruits and insects. The Coppersmith Barbet excavates nesting holes in dead branches and is a frequent participant in the chorus of tropical bird calls.",
    
    "Crested Serpent-Eagle": "A powerful raptor marked by a prominent crest on its head, the Crested Serpent-Eagle soars on thermals over forests and hilly terrain searching primarily for snakes and other reptiles. It has broad wings for soaring and a distinctive, whistling call heard in its Southeast Asian range. It nests high in large trees, often reusing old nests of other large birds, and maintains territories year-round.",
    "Eurasian Collared-Dove": "Pale grey with a distinctive black ring around the back of the neck, the Eurasian Collared-Dove is an adaptable bird often seen in open habitats and urban areas. Originally from Asia, it has successfully expanded its range globally. This dove feeds primarily on seeds and grains, often foraging on the ground in groups. It nests in trees and buildings close to human habitation.",
    
    "Eurasian Coot": "A waterbird with distinctive white frontal shield and beak contrasting with its black body, the Eurasian Coot is a strong swimmer with lobed feet. It inhabits lakes, ponds, and slow rivers, feeding on aquatic plants, insects, and small fish. Known to be territorial during breeding, this hardy bird often congregates in large flocks during migration and winter.",
    
    "Eurasian Hoopoe": "Recognizable by its striking crest of feathers and black-and-white wing pattern, the Eurasian Hoopoe uses its long, curved bill to probe soil for insects and larvae. Active in open woodlands, grasslands, and gardens across Eurasia and North Africa, its distinctive 'oop-oop-oop' call heralds early morning and late evening. Its elaborate courtship dance and nesting habits in cavity holes are remarkable.",
    
    "Eurasian Marsh-Harrier": "A large bird of prey that skims low over marshes and reedbeds, the Eurasian Marsh-Harrier has males with pale heads and females exhibiting mottled brown plumage. It hunts birds, small mammals, and amphibians. Widely distributed across Europe and Asia, it nests on the ground amidst dense reed beds and performs impressive aerial displays during breeding.",
    
    "Eurasian Moorhen": "Stocky and social, the Eurasian Moorhen sports a blackish body with a red frontal shield and yellow-tipped beak. It frequents freshwater wetlands where it grazes on aquatic plants and small animals. Aggressive in defending territory, it builds nests in dense vegetation near water. It is common across Eurasia and often seen swimming and walking near water edges.",
    
    "Garganey": "A small, migratory dabbling duck, the Garganey exhibits a distinctive white stripe over the eye and patterned plumage. It breeds in northern Europe and Asia and winters in Africa and South Asia. Preferring shallow freshwater habitats, it feeds on seeds, aquatic plants, and invertebrates. Its rapid flight and high-pitched calls are characteristic during migration.",
    
    "Glossy Ibis": "Wading bird with iridescent dark plumage that shines with green, purple, and bronze hues in sunlight. The Glossy Ibis probes mud and shallow waters with its long, curved bill to feed on insects, small fish, and crustaceans. Found in wetlands across Asia, it nests in colonies often with other wading birds and displays characteristic slow, deliberate flight.",
    
    "Gray Heron": "A tall, stately bird with a long neck and legs, the Gray Heron stands silently at the water’s edge before striking swiftly to catch fish and amphibians. Its predominantly gray plumage and black stripe over the eye make it easy to identify. The species is widely distributed across Europe and Asia and nests in communal breeding colonies, often near wetlands.",
    
    "Gray Wagtail": "Noted for its long tail that bobs as it walks or hovers near fast-flowing streams, the Gray Wagtail has grey upperparts and a yellowish underbelly. It feeds on insects and other invertebrates along riverbanks and in wet forests. It breeds in northern temperate zones and migrates south in winter, often seen in small groups or alone.",
    
    "Gray-breasted Prinia": "A small active bird common in grasslands and open woodlands with a distinctive gray breast and slender tail often held upright. It has a loud, repetitive song and feeds primarily on insects. The Gray-breasted Prinia builds neat ball-shaped nests in bushes and is widespread across South and Southeast Asia.",
    
    "Gray-headed Canary-Flycatcher": "Small, lively insectivore featuring a gray head and yellow-green body, the Gray-headed Canary-Flycatcher flits actively in forest canopies hunting flying insects. It prefers dense woodland and avoids open areas. Its sharp, high-pitched calls often precede its quick darting flights between perches.",
    
    "Great Egret": "The Great Egret is a large, elegant white heron with a long neck and yellow bill. It inhabits wetlands, lakes, and marshes, stalking fish, amphibians, and invertebrates with slow, deliberate movements. During breeding season, it displays spectacular long plumes on the back used to attract mates. This bird is widely distributed and a symbol of wetland ecosystems.",
    
    "Greater Coucal": "A large, crow-like member of the cuckoo family with glossy black wings and a rich chestnut body. The Greater Coucal roams open woodland, plantations, and gardens, feeding on insects, small reptiles, and eggs. It has a deep, booming call and is known for its skulking habits despite its size. It builds a large nest of sticks concealed in dense vegetation.",
    
    "Greater Racket-tailed Drongo": "Famed for its extraordinary crossed tail feathers with prominent circular shafts, the Greater Racket-tailed Drongo is jet black with a metallic blue sheen. It inhabits dense forests and is an adept mimic, often copying calls of other animals to deceive or intimidate. This fearless bird chases away large birds and feeds on insects, sometimes joining mixed bird flocks.",
    
    "Green Sandpiper": "A small, slim wader often found in freshwater marshes and puddles, the Green Sandpiper is dark brown above with a distinctive white rump noticeable in flight. It feeds on aquatic insects and larvae by probing mud and shallow water. It breeds in northern parts of Eurasia and winters in South Asia, showing wary and solitary behavior.",
    
    "Green Warbler": "A small leaf warbler with bright green upperparts and pale underparts, the Green Warbler inhabits forests and woodlands across Asia and migrates to warmer regions for winter. It feeds on insects gleaned from leaves and twigs, often producing sweet and varied songs. This bird is shy and tends to stay in the mid-canopy.",
    
    "Greenish Warbler": "Closely related to the Green Warbler, the Greenish Warbler shows a slightly greener tint and a distinctive melodic call. It breeds in temperate forests of Eurasia and migrates to tropical Asia in winter. This insectivore prefers dense foliage and is often heard before it is seen, fluttering actively while foraging.",
    
    "House Crow": "The House Crow is a highly intelligent and adaptable bird commonly found in urban and rural settlements. It has a distinctive grey neck and breast contrasting with the black head and body. Known for scavenging, it feeds on refuse, insects, small animals and food scraps, often seen in noisy groups. House Crows are very social and have complex vocal communication.",
    
    "House Sparrow": "A small, stout bird that thrives alongside humans worldwide. The House Sparrow sports a brown back with streaks and a grey belly, with males having distinctive black bibs. It feeds primarily on seeds and scraps of human food and nests in a variety of urban and rural structures. This species has adapted remarkably well to diverse environments.",
    
    "Kentish Plover": "A small shorebird with sandy brown upperparts and white underparts, the Kentish Plover frequents sandy beaches, salt flats, and riverbanks. It feeds by sight on insects, small crustaceans and worms. Breeding involves territorial displays and ground scrapes for nests, often camouflaged among stones and shells.",
    
    "Large-billed Crow": "Larger than the House Crow, this crow sports a stouter bill and all-black plumage with a slight bluish sheen. Found in various habitats from forests to urban areas, it is omnivorous, feeding on insects, carrion, seeds, and human refuse. Known for its adaptability and intelligence, it often forages in groups and exhibits complex social behavior.",
    
    "Laughing Dove": "A small, gentle dove with pinkish-brown body plumage and a subtle but distinct blue-grey head and black spotted collar. It inhabits dry and semi-arid regions, gardens, and scrubby areas. The Laughing Dove's soft cooing call resembles laughter and it feeds mostly on seeds, foraging on the ground.",
    
    "Little Egret": "A small white heron with slender black legs and yellow feet, the Little Egret hunts for fish and crustaceans by wading in shallow waters often alongside cattle. It performs characteristic foot-stirring to flush prey. Agile and graceful, it nests colonially with other egrets and herons, often showing elegant breeding plumes.",
    
    "Little Grebe": "Also called dabchick, this small waterbird has a compact body with brownish plumage and a sharp whistling call. It is an expert diver and swimmer, feeding on small fish and aquatic insects in ponds, lakes, and slow rivers. The Little Grebe builds floating nests concealed in emergent vegetation.",
    
    "Little Ringed Plover": "Small and active, this plover features a white ring around its eyes that stands out against its brown head. It prefers gravel or sandy riverbanks where it feeds on insects and small invertebrates by sight. During breeding, it performs elaborate displays to protect nesting territories on open ground.",
    
    "Little Spiderhunter": "A tiny, specialized nectar feeder with a long, curved bill perfectly adapted for extracting nectar from tubular flowers. It inhabits forests and gardens in tropical Asia, also feeding on small insects and spiders. Known for swift flight and skulking behavior, the Little Spiderhunter builds compact nests suspended among foliage.",
    
    "Pied Kingfisher": "A bold black and white kingfisher, the Pied Kingfisher uniquely hovers motionless over water before diving to catch fish. Found on rivers, lakes, and estuaries across Asia, it feeds mainly on small fish and amphibians. Highly social, it often forms flocks and nests colonially in sandbanks or earth banks.",
    
    "Plain Prinia": "A small, inconspicuous warbler with warm brown upperparts and paler underparts, the Plain Prinia is common in grasslands, scrub, and open woodland. It builds a ball-shaped nest in low bushes and feeds on insects. Its loud, repetitive calls make its presence known despite its modest appearance.",
    
    "Puff-throated Babbler": "A skulking bird with a puffed white throat and warm brown upperparts, the Puff-throated Babbler inhabits thick undergrowth and secondary forests. It moves in noisy groups, feeding on insects and small invertebrates in leaf litter and dense shrubs. This species is more often heard than seen due to its shy habits.",
    
    "Purple Heron": "Taller and more slender than the Gray Heron, the Purple Heron boasts a rich chestnut and purple-grey plumage with a long neck and sharp bill. It frequents dense reed beds and swamps, hunting mainly fish and amphibians stealthily from cover. It nests hidden among reeds and tall grasses, often colonial in distribution.",
    
    "Purple Sunbird": "Males of the Purple Sunbird exhibit iridescent purple-blue plumage while females are olive above with yellowish undersides. Nectarivorous but opportunistically insectivorous, this active little bird is widely distributed in gardens, scrub, and forests. Known for its acrobatic feeding and high-pitched calls, it breeds year-round in tropical Asia.",
    
    "Red-rumped Swallow": "Similar to the Barn Swallow but with a distinctive rufous patch on the rump, this swallow builds bowl-shaped mud nests under bridges, rocks, and buildings. It feeds on flying insects with agile, fast flight and prefers open country with water nearby. Migratory in some regions, it undertakes long-distance seasonal movements.",
    
    "Red-wattled Lapwing": "Easily identified by its loud calls and striking color pattern of black, white, and bright red wattles near the eyes, the Red-wattled Lapwing is a common sight in open farmland and grasslands across South Asia. Ground-nesting and highly protective, it feeds on insects and small invertebrates, often seen foraging alone or in pairs.",
    
    "Red-whiskered Bulbul": "This medium-sized bird has a distinctive red patch below the eye and a prominent crest atop its head. It inhabits tropical gardens and forests, feeding both on fruits and small insects. Vocal and active, the Red-whiskered Bulbul is a popular favorite among bird enthusiasts and adapts well to urban environments.",
    "Rock Pigeon": "A ubiquitous presence in cities and towns, the Rock Pigeon is highly adaptable with considerable plumage variation ranging from blue-gray to white and mottled patterns. Originally cliff dwellers, they have successfully colonized urban environments, nesting on ledges and buildings. Rock Pigeons primarily feed on seeds and grains and are known for their strong homing instincts.",
    
    "Rose-ringed Parakeet": "Known for its bright green body and distinctive colored neck ring found on males, the Rose-ringed Parakeet is a noisy and gregarious parrot frequenting gardens, woodlands, and cultivated areas. It feeds on fruits, nuts, seeds, and flowers and is especially famous for its adaptability to urban life. This species has become an introduced, breeding population in many cities globally.",
    
    "Rufous Treepie": "Distinctive with its rust-red body and long black tail and wings, the Rufous Treepie is a vocal and intelligent bird common throughout open forests and gardens. It has a varied diet including insects, small reptiles, fruits, and eggs. Its loud and sharp calls are often heard from high perches where it surveys for potential food and threats.",
    
    "Scaly-breasted Munia": "A small finch with elaborate scaled patterning on the breast and belly, the Scaly-breasted Munia frequents grasslands, reed beds, and agricultural landscapes. It feeds mainly on grass seeds and grains often in large flocks. This species is popular in the pet trade and is known for its sociable behavior and distinctive bubbling calls.",
    
    "Spotted Dove": "A gentle, soft-cooing dove with pale brown plumage and a distinctive black and white spotted collar around the neck. It inhabits a variety of open woodlands, gardens, and fields. Feeding mostly on seeds and grains, it frequently forages on the ground alone or in pairs. The Spotted Dove is widespread and often unnoticed due to its quiet and reserved demeanor.",
    
    "Stork-billed Kingfisher": "One of the largest kingfishers, this bird has a magnificent large red bill and a stunning mix of blue wings and back with a rufous head and breast. Preferring large forest streams and lakes, it hunts fish, frogs, and crustaceans from a perch. It nests in tunnels excavated in riverbanks and is typically solitary, maintaining well-defined territories.",
    
    "Tickell's Blue Flycatcher": "A small and brightly colored bird featuring azure blue upperparts and warm orange underparts, Tickell's Blue Flycatcher inhabits dense tropical forests and thick scrub. Often heard before seen, it emits a series of melodious whistles and chirps. Its diet consists primarily of insects, which it catches with acrobatic flight or gleans from foliage.",
    
    "Western Yellow Wagtail": "A slender and lively insect-eating bird with bright yellow belly and variable head patterns depending on subspecies. It prefers wet meadows, agricultural fields, and grasslands in its Northern Hemisphere breeding range. During winter, it migrates to warmer tropical areas, feeding on a variety of insects both on the ground and in shallow water.",
    
    "Whiskered Tern": "A graceful tern characterized by its black head and greyish body during breeding season. It is commonly seen over freshwater lakes and reservoirs where it feeds by diving for fish and aquatic insects. Whiskered Terns nest in colonies on floating vegetation or marsh islands and emit soft, trilling calls while in flight.",
    
    "White-breasted Waterhen": "A conspicuous waterbird with contrasting black and white plumage and bright yellow legs, the White-breasted Waterhen lives in dense marshes, swamps, and flooded fields. It feeds on insects, snails, and aquatic plants by walking through shallow water and mud. The species is vocal and territorial, often heard before seen due to its loud, distinctive calls.",
    
    "White-throated Kingfisher": "Recognizable by its brilliant blue back and wings, bright white throat, and large red bill, this kingfisher inhabits a wide range of habitats beyond water including farmland and gardens. It feeds on fish, frogs, insects, and small reptiles, hunting from exposed perches. Its loud, harsh call is a notable sound in many tropical landscapes.",
    
    "Wood Sandpiper": "A delicate and nervously active wader with brown back and white underparts, the Wood Sandpiper frequents muddy wetlands, marshes, and flooded fields. It feeds on aquatic insects and small invertebrates by probing mud and shallow water. This species breeds in northern Eurasia and migrates to tropical and southern Asia for wintering grounds.",
    
    "Zitting Cisticola": "A small, discreet bird known for its rapid repetitive 'zitting' call resembling a series of clicks. It thrives in grassy fields, open grasslands, and scrub areas, often perched atop tall grass stalks. The Zitting Cisticola builds compact, ball-shaped nests woven into grass stems and feeds mainly on small insects and spiders."
}

def bird_description(common_name: str) -> str:
    return BIRD_DESCRIPTIONS.get(common_name, "Description not available yet.")

def scientific_name(common_name: str, df: pd.DataFrame) -> str:
    sub = df[df["common_name"] == common_name]
    if sub.empty or "scientific_name" not in sub.columns:
        return "Unknown"
    return sub["scientific_name"].iloc[0]

def _svg_to_dataurl(path_to_svg: str) -> str:
    if not os.path.exists(path_to_svg):
        return ""
    with open(path_to_svg, "r", encoding="utf-8") as f:
        svg = f.read()
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")

@st.cache_data
def _icon_dataurl():
    return _svg_to_dataurl(SVG_CROW)

def heatmap_folium(common_name: str, df: pd.DataFrame, width: int = 900):
    bird_data = df[df["common_name"] == common_name]
    if bird_data.empty:
        st.info("No records for this species.")
        return

    lat = bird_data["latitude"].mean()
    lon = bird_data["longitude"].mean()
    if pd.isna(lat) or pd.isna(lon):
        st.info("No coordinates to display.")
        return

    m = folium.Map(location=[lat, lon], zoom_start=5, control_scale=True)

    marker_cluster = plugins.MarkerCluster().add_to(m)
    icon_url = _icon_dataurl()
    for _, row in bird_data.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.CustomIcon(icon_image=icon_url, icon_size=(30, 30)) if icon_url else None,
            popup=f"Common Name: {row['common_name']} | Species: {row['primary_label']}",
        ).add_to(marker_cluster)

    heat_data = bird_data[["latitude", "longitude"]].values.tolist()
    plugins.HeatMap(heat_data).add_to(m)

    folium.LayerControl().add_to(m)
    folium_static(m, width=width)

def map_3d_deck(common_name: str, df: pd.DataFrame):
    data = df[df["common_name"] == common_name][["latitude", "longitude", "common_name"]].copy()
    if data.empty:
        return None

    data["lat"] = data["latitude"].astype(float)
    data["lon"] = data["longitude"].astype(float)

    view_state = pdk.ViewState(
        latitude=float(data["lat"].mean()),
        longitude=float(data["lon"].mean()),
        zoom=4,
        pitch=45,
        bearing=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position="[lon, lat]",
        get_radius=20000,
        get_color=[50, 180, 255],
        pickable=True,
        auto_highlight=True,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Common Name: {common_name}"},
        map_style="mapbox://styles/mapbox/light-v9",
    )
    return deck
