from PIL import Image,ImageDraw,ImageFont,ImageFilter
import random

def gen_check_code(width=120,height=30,char_lenth=5,font_size=28):
    img=Image.new(mode='RGB',color=(255,255,255),size=(width,height))
    draw=ImageDraw.Draw(img,mode='RGB')
    #generate a random character
    def ran_char():
        return chr(random.randint(65,90))
    #generate a random three_tuple contains the color band
    def ran_col():
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    #Let's say draw five characters in the image
    #generate a random font
    def ran_font():
        fonts=(r'utils/check_code/kumo.ttf',r'utils/check_code/domi.ttf',r'utils/check_code/Monaco.ttf')
        index=random.randint(0,2)  #note,both side include
        font = ImageFont.truetype(font=fonts[index], size=font_size)
        return font
    # draw the text(5 characters)
    code=''
    for i in range(char_lenth):
        char=ran_char()
        code=code+char
        col=ran_col()
        xy=[i*width/char_lenth,random.randint(0,4)]
        font=ran_font()
        draw.text(xy=xy,fill=col,text=char,font=font)
    #draw a bunch of dots
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=ran_col())
    # draw the line
    # start_point
    x1=width/2/random.randint(1,10)
    y1=height/2/random.randint(1,10)
    #end_point
    x2=x1+60
    y2=y1+15
    xy=[x1,y1,x2,y2]
    draw.line(xy,fill=ran_col())

    # draw a bunch of arcs
    for i in range(0,10):
        x1=random.randint(0,width-10)
        y1=random.randint(0,height-10)
        x2=x1+2
        y2=y1+2
        draw.arc(xy=[x1,y1,x2,y2],start=0,end=90,fill=ran_col())

    img=img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return code,img


