from images.images import images
import basilisk as bsk
import glm

engine = bsk.Engine()
scene = bsk.Scene(engine)
scene.sky = None

# load fish
names = ['battery', 'squid', 'picture_frame']
materials = [bsk.Material(texture = images[f'{name}.png']) for name in names]
meshes = [bsk.Mesh(f'./meshes/{name}.obj') for name in names]

for i, (mesh, material) in enumerate(zip(meshes, materials)):
    scene.add(bsk.Node(
        position = (0, i * 3, 0),
        mesh = mesh,
        material = material
    ))

while engine.running:
    scene.update()
    engine.update()