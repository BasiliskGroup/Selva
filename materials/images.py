from basilisk import Image
import os

images = {
    file_name : Image(f'./materials/{file_name}') 
    for file_name in os.listdir('./materials') 
    if file_name.endswith(('.png', '.jpeg', '.jpg'))
}