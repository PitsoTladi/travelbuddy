import csv
import io
import secrets
from datetime import timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from users.models import User
from interests.models import Interest
from destinations.models import Destination
from events.models import Event, Attendance
from reviews.models import review
from posts.models import Post

INTERESTS = ["Adventure", "Nature", "Culture", "History", "Food", "Art",
             "Music", "Nightlife", "Family", "Wildlife", "Hiking", "Sports"]

PEOPLE = [
("Ayesha Khan","ayesha.khan","adventure_seeker","Weekend hiker, curious traveller and amateur food critic.",1800),
("Liam Mokoena","liam.mokoena","adventure_seeker","Always looking for a new trail, view or road trip.",2500),
("Thandi Ndlovu","thandi.ndlovu","adventure_seeker","I travel for the stories, people and local food.",1200),
("Daniel Jacobs","daniel.jacobs","adventure_seeker","Photographer chasing golden hour around South Africa.",3000),
("Zanele Dlamini","zanele.dlamini","adventure_seeker","Culture, live music and spontaneous city adventures.",1500),
("Musa Nkosi","musa.nkosi","adventure_seeker","Nature lover. Give me mountains over malls.",2200),
("Chloe Smith","chloe.smith","adventure_seeker","Finding family-friendly places and hidden gems.",2000),
("Sipho Khumalo","sipho.khumalo","adventure_seeker","Football, food markets and exploring neighbourhoods.",1000),
("Naledi Molefe","naledi.molefe","adventure_seeker","Art galleries, design markets and beautiful spaces.",1600),
("Ethan Botha","ethan.botha","adventure_seeker","An outdoors person with a soft spot for history.",2800),
("Amara Patel","amara.patel","adventure_seeker","Trying a new restaurant or experience every month.",1400),
("Kabelo Maseko","kabelo.maseko","adventure_seeker","Cycling, hiking and taking the scenic route.",1900),
("Olivia Naidoo","olivia.naidoo","adventure_seeker","Travel journal enthusiast and wildlife fan.",2600),
("Lerato Sithole","lerato.sithole","adventure_seeker","I love festivals, theatre and local experiences.",1700),
("Noah van der Merwe","noah.vdm","adventure_seeker","Budget-conscious traveller, big on memorable experiences.",900),
("Keisha Williams","keisha.williams","business_creator","Creating welcoming spaces and memorable local experiences.",0),
("Bongani Zulu","bongani.zulu","business_creator","Small-business owner passionate about responsible tourism.",0),
("Mia Botha","mia.botha","event_creator","Bringing communities together through creative events.",0),
("Tshepo Radebe","tshepo.radebe","event_creator","Event organiser focused on music, food and culture.",0),
("Priya Govender","priya.govender","event_creator","Building experiences that make people explore their city.",0),
]

# name, address, description, price, interest, city, longitude, latitude
DESTINATIONS = [
("Walter Sisulu Botanical Garden","Roodepoort, Johannesburg","Green escape with walking paths, birdlife and the Witpoortjie waterfall.",70,"Nature","Johannesburg",27.8370,-26.0945),
("Constitution Hill","Braamfontein, Johannesburg","Explore South Africa's constitutional history through exhibitions and tours.",100,"History","Johannesburg",28.0392,-26.1885),
("Apartheid Museum","Northern Parkway, Johannesburg","A powerful museum documenting apartheid and the road to democracy.",150,"History","Johannesburg",28.0094,-26.2357),
("Johannesburg Botanical Garden","Emmarentia, Johannesburg","Peaceful urban garden with lawns, trees and a popular dam.",0,"Nature","Johannesburg",28.0094,-26.1617),
("Maboneng Precinct","Maboneng, Johannesburg","Creative district filled with street art, independent shops and restaurants.",100,"Art","Johannesburg",28.0587,-26.2041),
("Soweto Towers","Orlando East, Soweto","Iconic cooling towers transformed into an adventure landmark.",150,"Adventure","Johannesburg",27.9094,-26.2367),
("Cradle of Humankind","Maropeng, Gauteng","Discover one of the world's most important hominin fossil sites.",120,"History","Johannesburg",27.6580,-25.9690),
("Lion and Safari Park","Broederstroom, Hartbeespoort","Wildlife experience in a conservation setting.",250,"Wildlife","Hartbeespoort",27.8660,-25.8350),
("Union Buildings","Government Avenue, Pretoria","Admire the architecture and landscaped gardens at the seat of government.",0,"History","Pretoria",28.2110,-25.7400),
("Freedom Park","Salvokop, Pretoria","Heritage destination honouring people and stories that shaped South Africa.",80,"Culture","Pretoria",28.1950,-25.7550),
("Voortrekker Monument","Eeufees Road, Pretoria","Heritage site with exhibitions and panoramic views.",100,"History","Pretoria",28.1750,-25.7760),
("Gold Reef City","Ormonde, Johannesburg","Theme park and heritage attraction built around gold-mining history.",250,"Family","Johannesburg",28.0110,-26.2350),
("Johannesburg Zoo","Parkview, Johannesburg","Urban zoo with a wide range of animal species.",120,"Wildlife","Johannesburg",28.0410,-26.1660),
("Melville Koppies","Melville, Johannesburg","Nature reserve with hiking trails and archaeological features.",80,"Hiking","Johannesburg",28.0030,-26.1740),
("Neighbourgoods Market","Braamfontein, Johannesburg","Weekend market for street food, local produce and socialising.",0,"Food","Johannesburg",28.0340,-26.1920),
("Victoria Yards","Lorentzville, Johannesburg","Creative precinct supporting artists, makers and urban agriculture.",0,"Art","Johannesburg",28.0670,-26.1950),
("Kirstenbosch Gardens","Newlands, Cape Town","World-renowned botanical gardens beneath Table Mountain.",120,"Nature","Cape Town",18.4320,-33.9880),
("Table Mountain Cableway","Tafelberg Road, Cape Town","Spectacular views of Cape Town from the top of Table Mountain.",430,"Adventure","Cape Town",18.4090,-33.9620),
("V&A Waterfront","Cape Town Harbour","Waterfront destination with shops, restaurants and harbour views.",0,"Food","Cape Town",18.4204,-33.9036),
("Robben Island Museum","Nelson Mandela Gateway, Cape Town","Historic island prison associated with Nelson Mandela.",600,"History","Cape Town",18.3667,-33.8067),
("Boulders Beach","Simon's Town, Cape Town","Sheltered beach known for its African penguin colony.",190,"Wildlife","Cape Town",18.4510,-34.1970),
("Company's Garden","Central Cape Town","Historic public garden surrounded by museums and heritage buildings.",0,"Nature","Cape Town",18.4160,-33.9250),
("uShaka Marine World","Point, Durban","Marine theme park and aquarium on Durban's Golden Mile.",220,"Family","Durban",31.0450,-29.8660),
("Moses Mabhida Stadium","Stamford Hill, Durban","Landmark stadium offering tours and adventure activities.",100,"Sports","Durban",31.0300,-29.8270),
("Durban Botanic Gardens","Berea, Durban","One of Africa's oldest surviving botanical gardens.",0,"Nature","Durban",31.0090,-29.8580),
("Golden Mile Beachfront","North Beach, Durban","Lively beachfront promenade for walking, cycling and ocean views.",0,"Adventure","Durban",31.0360,-29.8480),
("The Big Hole","New Park, Kimberley","Historic diamond mine excavation and surrounding museum.",120,"History","Kimberley",24.7630,-28.7380),
("Addo Elephant National Park","Addo, Eastern Cape","Conservation area known for elephants and diverse wildlife.",120,"Wildlife","Gqeberha",25.7460,-33.4440),
("Cango Caves","Oudtshoorn, Western Cape","Spectacular limestone chambers and formations on guided tours.",180,"Adventure","Oudtshoorn",22.2170,-33.3920),
("Blyde River Canyon","Mpumalanga","Dramatic canyon scenery, viewpoints and hiking opportunities.",0,"Hiking","Graskop",30.8000,-24.5900),
]

EVENTS = [
("Soweto Street Food Walk","Sample local favourites and hear stories about Soweto's food culture.","Food","Johannesburg","Vilakazi Street, Soweto",180),
("Braamfontein Art Crawl","An afternoon exploring galleries, murals and creative spaces.","Art","Johannesburg","Braamfontein, Johannesburg",80),
("Sunset Hike at Melville Koppies","A guided evening walk with views across the city.","Hiking","Johannesburg","Melville Koppies, Johannesburg",120),
("Maboneng Live Music Night","Local performers, good company and a lively city atmosphere.","Music","Johannesburg","Maboneng, Johannesburg",150),
("Constitution Hill Heritage Tour","A guided introduction to the history behind the constitution.","History","Johannesburg","Constitution Hill, Johannesburg",100),
("Family Nature Discovery","A relaxed outdoor discovery day for younger explorers.","Family","Johannesburg","Walter Sisulu Botanical Garden",90),
("Pretoria Heritage Walk","Explore the capital's architecture, monuments and history.","Culture","Pretoria","Union Buildings, Pretoria",80),
("Hartbeespoort Wildlife Morning","A guided wildlife experience and conservation conversation.","Wildlife","Hartbeespoort","Hartbeespoort, North West",250),
("Cape Town Coastal Walk","A scenic group walk with ocean views and photo stops.","Nature","Cape Town","Sea Point Promenade, Cape Town",0),
("Table Mountain Sunrise Meetup","Start early and enjoy the mountain before the city gets busy.","Adventure","Cape Town","Table Mountain, Cape Town",100),
("Durban Beach Sports Day","Friendly beach games and a relaxed social atmosphere.","Sports","Durban","Golden Mile, Durban",50),
("Durban Food Market Social","Discover local flavours and meet fellow food lovers.","Food","Durban","Florida Road, Durban",100),
("Kimberley Diamond History Talk","A hosted session on the diamond rush and its legacy.","History","Kimberley","The Big Hole, Kimberley",70),
("Addo Wildlife Photography Day","A beginner-friendly wildlife photography outing.","Wildlife","Gqeberha","Addo Elephant National Park",300),
("Cango Caves Adventure Tour","Explore underground chambers with an experienced guide.","Adventure","Oudtshoorn","Cango Caves, Oudtshoorn",180),
]

def artwork(title, subtitle, seed, avatar=False):
    # Generated illustrative artwork; no external image service required.
    from PIL import Image, ImageDraw
    import random
    rng = random.Random(seed)
    w, h = (420, 420) if avatar else (900, 560)
    palette = [(25,75,95),(44,95,75),(105,75,125),(155,95,55),(45,105,135),(105,115,65),(135,70,75),(65,85,125)]
    a = palette[seed % len(palette)]
    b = tuple(min(255, v+70) for v in a)
    im = Image.new("RGB", (w,h))
    px = im.load()
    for y in range(h):
        t=y/(h-1)
        c=tuple(int(a[k]*(1-t)+b[k]*t) for k in range(3))
        for x in range(w): px[x,y]=c
    d=ImageDraw.Draw(im, "RGBA")
    for layer in range(5):
        y0=int(h*(0.48+layer*0.08))
        pts=[(0,h),(0,y0)]
        pts += [(x,y0+rng.randint(-28,28)) for x in range(0,w+40,40)]
        pts += [(w,h)]
        d.polygon(pts, fill=(8+layer*13,28+layer*12,35+layer*10,120))
    if avatar:
        d.ellipse((120,55,300,235), fill=(244,211,177,255))
        d.rounded_rectangle((65,215,355,470), radius=110, fill=(235,235,225,255))
    else:
        d.rounded_rectangle((35,h-150,w-35,h-30), radius=22, fill=(0,0,0,135))
        try:
            f=ImageFont.truetype("arial.ttf",38)
            sf=ImageFont.truetype("arial.ttf",23)
        except OSError:
            f=sf=ImageFont.load_default()
        d.text((62,h-132),title[:36],font=f,fill="white")
        d.text((62,h-75),subtitle[:50],font=sf,fill=(235,240,240,255))
    out=io.BytesIO()
    im.save(out,format="JPEG",quality=88)
    return out.getvalue()

class Command(BaseCommand):
    help = "Seed TravelBuddySA with demo users, destinations, events and community activity."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        interests={}
        for name in INTERESTS:
            interests[name],_=Interest.objects.get_or_create(name=name)

        csv_path=Path(settings.BASE_DIR)/"demo_user_credentials.csv"
        csv_exists=csv_path.exists()
        new_credentials=[]
        users=[]
        for i,(name,username,role,bio,budget) in enumerate(PEOPLE):
            email=f"{username}@travelbuddy-demo.local"
            user,created=User.objects.get_or_create(username=username,defaults={
                "name":name,"email":email,"role":role,"bio":bio,"budget":budget,
                "review_points":(i*7)%201,
            })
            if created:
                password="TB!"+secrets.token_urlsafe(12)
                user.set_password(password)
                user.avatar.save(f"{username}.jpg",ContentFile(artwork(name,role,i,True)),save=False)
                user.save()
                new_credentials.append([username,email,password,role])
            users.append(user)

        if new_credentials:
            with csv_path.open("a" if csv_exists else "w",newline="",encoding="utf-8") as f:
                writer=csv.writer(f)
                if not csv_exists: writer.writerow(["username","email","password","role"])
                writer.writerows(new_credentials)

        seekers=[u for u in users if u.role=="adventure_seeker"]
        businesses=[u for u in users if u.role=="business_creator"]
        event_creators=[u for u in users if u.role=="event_creator"]
        for i,u in enumerate(users):
            u.interests.set([interests[n] for n in [INTERESTS[(i+j*3)%len(INTERESTS)] for j in range(3)]])

        destinations=[]
        for i,(name,address,desc,price,interest,city,lon,lat) in enumerate(DESTINATIONS):
            obj,_=Destination.objects.get_or_create(name=name,defaults={
                "address":address,"description":desc,"price":price,
                "interest":interests[interest],"city":city,"longitude":lon,"latitude":lat,
                "rating":round(3.5+(i%15)/10,2),"created_by":businesses[i%len(businesses)],
            })
            if not obj.image:
                obj.image.save(f"destination_{i+1:02d}.jpg",ContentFile(artwork(name,city,100+i)),save=True)
            destinations.append(obj)

        events=[]
        today=timezone.localdate()
        for i in range(30):
            name,desc,interest,city,address,price=EVENTS[i%len(EVENTS)]
            if i>=len(EVENTS): name=f"{name} - Edition {i//len(EVENTS)+1}"
            dest=destinations[(i*3)%len(destinations)]
            obj,_=Event.objects.get_or_create(name=name,defaults={
                "address":address,"description":desc,"created_by":event_creators[i%len(event_creators)],
                "price":price,"city":city,"category":interest,"destination":dest,
                "start_date":today+timedelta(days=7+i*3),"end_date":today+timedelta(days=7+i*3),
                "capacity":20+(i%8)*10,"longitude":dest.longitude,"latitude":dest.latitude,
            })
            obj.interest.set([interests[interest],interests["Culture"]])
            if not obj.image:
                obj.image.save(f"event_{i+1:02d}.jpg",ContentFile(artwork(name,city,200+i)),save=True)
            events.append(obj)

        for i,event in enumerate(events):
            for offset in range(3):
                Attendance.objects.get_or_create(event=event,user=seekers[(i+offset*4)%len(seekers)])

        for i in range(36):
            user=seekers[i%len(seekers)]
            if i%2==0:
                target={"destination":destinations[i%len(destinations)],"event":None}
                label=destinations[i%len(destinations)].name
            else:
                target={"destination":None,"event":events[i%len(events)]}
                label=events[i%len(events)].name
            review.objects.get_or_create(created_by=user,rating=4+(i%2),
                content=f"{label} was memorable. Great atmosphere and well worth exploring.",**target)

        for i in range(20):
            user=seekers[i%len(seekers)]
            dest=destinations[(i*2)%len(destinations)]
            Post.objects.get_or_create(created_by=user,title=f"My TravelBuddy find: {dest.name}"[:100],
                defaults={"content":f"I visited {dest.name}. {dest.description or ''}"[:100],
                          "destination":dest})

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {len(users)} demo users, {len(destinations)} destinations, "
            f"{len(events)} events, {Attendance.objects.count()} attendance records, "
            f"{review.objects.count()} reviews and {Post.objects.count()} posts."
        ))
        if new_credentials:
            self.stdout.write(self.style.WARNING(f"New passwords saved to {csv_path}"))
        else:
            self.stdout.write("Existing demo users were kept; their passwords were not changed.")
