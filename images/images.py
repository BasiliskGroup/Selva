from basilisk import Image
import os

images = {
    file_name : Image(f'./images/{file_name}') 
    for file_name in os.listdir('./images') 
    if file_name.endswith(('.png', '.jpeg', '.jpg'))
}