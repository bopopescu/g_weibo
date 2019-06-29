from PIL import Image,ImageDraw
im = Image.open("1.jpg")
im_array = im.load()
print(im.size)
print(im_array)
new_im = Image.new("RGB",im.size)
draw = ImageDraw.Draw(new_im)
for x in range(1,im.size[0]):
    for y in range(1,im.size[1]):
        draw.point((x,y), fill=(im_array[x,y][0]-im_array[x-1,y][0]+im_array[x,y][1]-im_array[x-1,y][1]+im_array[x,y][2]-im_array[x-1,y][2],0,0))

new_im.save("rgb4.jpg","jpeg")
new_im.show()