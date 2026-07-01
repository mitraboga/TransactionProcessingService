from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap, math

OUT = Path('/mnt/data/midas_diagrams/assets/architecture')
OUT.mkdir(parents=True, exist_ok=True)
try:
    FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
    BOLD = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    SMALL = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 21)
except:
    FONT=BOLD=SMALL=None

BG='white'; BOX='#eef5ff'; STROKE='#23456b'; TEXT='#111827'; ACCENT='#dbeafe'; DB='#fef3c7'; API='#ecfdf5'; BAD='#fee2e2'; GOOD='#dcfce7'

def wrap(text, width=18):
    return '\n'.join(textwrap.wrap(text, width=width, break_long_words=False))

def box(draw, xy, text, fill=BOX, font=FONT, title=False, radius=16):
    x1,y1,x2,y2=xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=STROKE, width=3)
    lines=text.split('\n')
    f=BOLD if title else FONT
    total=sum(draw.textbbox((0,0),ln,font=f)[3]-draw.textbbox((0,0),ln,font=f)[1] for ln in lines) + (len(lines)-1)*6
    y=y1+(y2-y1-total)/2
    for ln in lines:
        bb=draw.textbbox((0,0),ln,font=f)
        draw.text((x1+(x2-x1-(bb[2]-bb[0]))/2,y),ln,fill=TEXT,font=f)
        y += (bb[3]-bb[1])+6

def arrow(draw, a, b, text=None):
    draw.line([a,b], fill=STROKE, width=4)
    ang=math.atan2(b[1]-a[1], b[0]-a[0]); L=14
    pts=[b,(b[0]-L*math.cos(ang-math.pi/6), b[1]-L*math.sin(ang-math.pi/6)),(b[0]-L*math.cos(ang+math.pi/6), b[1]-L*math.sin(ang+math.pi/6))]
    draw.polygon(pts, fill=STROKE)
    if text:
        mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
        draw.text((mx+8,my-26), text, fill=TEXT, font=SMALL)

def title(draw, t, w):
    bb=draw.textbbox((0,0),t,font=BOLD)
    draw.text(((w-(bb[2]-bb[0]))/2,30),t,fill=TEXT,font=BOLD)

# 1 overall
img=Image.new('RGB',(1800,1100),BG); d=ImageDraw.Draw(img); title(d,'Midas Core Overall Architecture',1800)
boxes={
'producer':(60,190,360,310,'Transaction Producer\n/ Frontend',BOX),
'kafka':(430,190,760,310,'Apache Kafka Topic\ntrader-updates',DB),
'listener':(850,150,1190,270,'TransactionListener\nSpring Kafka Consumer',BOX),
'validation':(850,330,1190,450,'Validation Logic\nIDs + balance check',BOX),
'incentive':(1280,260,1660,380,'External Incentive API\nPOST /incentive',API),
'balances':(850,520,1190,640,'Balance Update\namount + incentive',BOX),
'db':(850,730,1190,870,'H2 In-Memory DB\nUserRecord + TransactionRecord',DB),
'controller':(1280,620,1660,740,'BalanceController\nGET /balance',BOX),
'client':(1280,840,1660,960,'Balance Client\nJSON Response',BOX)
}
for k,(x1,y1,x2,y2,t,c) in boxes.items(): box(d,(x1,y1,x2,y2),t,c)
arrow(d,(360,250),(430,250)); arrow(d,(760,250),(850,210)); arrow(d,(1020,270),(1020,330)); arrow(d,(1190,390),(1280,320),'valid'); arrow(d,(1020,450),(1020,520)); arrow(d,(1020,640),(1020,730)); arrow(d,(1190,800),(1280,690)); arrow(d,(1470,740),(1470,840)); arrow(d,(1280,900),(1190,800)); arrow(d,(1280,320),(1190,570),'incentive')
img.save(OUT/'overall_architecture.png')

# 2 sprint pipeline
img=Image.new('RGB',(1800,800),BG); d=ImageDraw.Draw(img); title(d,'Five-Week Sprint Delivery Pipeline',1800)
xs=[70,420,770,1120,1470]; names=['Week 1\nFoundation\nJava 17 + Maven','Week 2\nKafka\nEvent Ingestion','Week 3\nDatabase\nJPA + Validation','Week 4\nIncentives\nREST Integration','Week 5\nBalance API\nGo-Live Readiness']
for i,x in enumerate(xs):
    box(d,(x,190,x+260,340),names[i],ACCENT, title=False)
    box(d,(x,470,x+260,620),f'Engineering Report\nSprint {i+1} Deliverables\nTest Verification',BOX)
    arrow(d,(x+130,340),(x+130,470))
    if i<4: arrow(d,(x+260,265),(xs[i+1],265))
img.save(OUT/'sprint_pipeline.png')

# 3 kafka flow
img=Image.new('RGB',(1500,900),BG); d=ImageDraw.Draw(img); title(d,'Kafka Transaction Consumption Flow',1500)
flow=[('Transaction\nProducer',BOX),('Kafka Topic\ntrader-updates',DB),('@KafkaListener\nTransactionListener.listen',BOX),('JSON Deserialize\nto Transaction',API),('senderId\nrecipientId\namount',BOX),('Validation\nPipeline',GOOD)]
y=180
for i,(t,c) in enumerate(flow):
    box(d,(520,y,980,y+90),t,c)
    if i>0: arrow(d,(750,y-60),(750,y))
    y+=150
img.save(OUT/'kafka_flow.png')

# 4 validation
img=Image.new('RGB',(1500,1100),BG); d=ImageDraw.Draw(img); title(d,'Transaction Validation Decision Flow',1500)
box(d,(560,120,940,220),'Kafka Transaction\nReceived',BOX)
box(d,(560,300,940,400),'Sender ID\nExists?',ACCENT)
box(d,(560,480,940,580),'Recipient ID\nExists?',ACCENT)
box(d,(560,660,940,760),'Sender Balance\n>= Amount?',ACCENT)
box(d,(560,840,940,940),'Valid Transaction\nPersist + Update',GOOD)
for y1,y2 in [(220,300),(400,480),(580,660),(760,840)]: arrow(d,(750,y1),(750,y2),'Yes' if y1>220 else None)
for y,t in [(330,'Discard\nInvalid Sender'),(510,'Discard\nInvalid Recipient'),(690,'Discard\nInsufficient Funds')]:
    box(d,(1030,y-40,1390,y+60),t,BAD)
    arrow(d,(940,y),(1030,y),'No')
img.save(OUT/'transaction_validation.png')

# 5 incentive sequence
img=Image.new('RGB',(1700,950),BG); d=ImageDraw.Draw(img); title(d,'Incentive API Sequence',1700)
parts=[('Kafka Listener',180),('Validation Logic',540),('Incentive API\nlocalhost:8080',900),('H2 Database',1260)]
for name,x in parts:
    box(d,(x,140,x+260,220),name,ACCENT if 'API' not in name and 'Database' not in name else (API if 'API' in name else DB))
    d.line([(x+130,220),(x+130,850)], fill='#9ca3af', width=2)
steps=[(310,310,'Validate Transaction'),(670,420,'Transaction valid'),(1030,530,'POST /incentive\nTransaction JSON'),(1030,640,'Incentive { amount }'),(1390,750,'Save balances\n+ TransactionRecord')]
arrow(d,(310,310),(670,310),'validate'); arrow(d,(670,420),(310,420),'valid'); arrow(d,(310,530),(1030,530),'POST'); arrow(d,(1030,640),(310,640),'response'); arrow(d,(310,750),(1390,750),'persist')
img.save(OUT/'incentive_api_sequence.png')

# 6 persistence
img=Image.new('RGB',(1700,1000),BG); d=ImageDraw.Draw(img); title(d,'Persistence Workflow and JPA Relationships',1700)
box(d,(650,120,1050,220),'Validated Transaction',GOOD)
box(d,(260,340,610,460),'Sender UserRecord\nDebit amount',BOX)
box(d,(1090,340,1440,460),'Recipient UserRecord\nCredit amount + incentive',BOX)
box(d,(650,340,1050,460),'TransactionRecord\namount + incentive',BOX)
box(d,(650,600,1050,720),'Many-to-One\nsender + recipient',ACCENT)
box(d,(650,810,1050,930),'H2 Database\nUser + Transaction tables',DB)
arrow(d,(650,220),(435,340)); arrow(d,(1050,220),(1265,340)); arrow(d,(850,220),(850,340)); arrow(d,(850,460),(850,600)); arrow(d,(435,460),(720,810)); arrow(d,(1265,460),(980,810)); arrow(d,(850,720),(850,810))
img.save(OUT/'persistence_flow.png')

# 7 balance endpoint
img=Image.new('RGB',(1700,950),BG); d=ImageDraw.Draw(img); title(d,'Balance Endpoint REST Sequence',1700)
parts=[('Client',180),('BalanceController',540),('UserRepository',900),('H2 Database',1260)]
for name,x in parts:
    box(d,(x,140,x+260,220),name,DB if 'Database' in name else ACCENT)
    d.line([(x+130,220),(x+130,850)], fill='#9ca3af', width=2)
arrow(d,(310,310),(670,310),'GET /balance?userId=id')
arrow(d,(670,430),(1030,430),'findById(userId)')
arrow(d,(1030,550),(1390,550),'query UserRecord')
arrow(d,(1390,660),(1030,660),'UserRecord or empty')
arrow(d,(1030,760),(670,760),'Optional<UserRecord>')
arrow(d,(670,840),(310,840),'Balance JSON')
img.save(OUT/'balance_endpoint_flow.png')

print('done')
