import basilisk as bsk
import glm

engine = bsk.Engine()
scene = bsk.Scene(engine)
node = bsk.Node()
scene.add(node)

static = bsk.StaticCamera()
free = scene.camera

looked = False

def key_pressed(key):
    return engine.keys[key] and not engine.previous_keys[key]

def actions(looked) -> bool:
    
    if not looked and engine.mouse.left_click:
        cast = scene.raycast_mouse((engine.mouse.x, engine.mouse.y))
        if not cast.node: return looked
        looked = True
        scene.camera = static
        # set item position
        return looked
    
    rel_x, rel_y = engine.mouse.relative
    if looked and engine.mouse.left_down:
        if rel_x != 0 or rel_y != 0:
            sensitivity = 0.25
            node.rotational_velocity = scene.camera.rotation * glm.vec3(rel_y * sensitivity, rel_x * sensitivity, 0)
            
    if looked and key_pressed(bsk.pg.K_e):
        looked = False
        scene.camera = free
        # reset item position
        
    return looked
        
def update_node(dt: float) -> None:
    node.rotational_velocity = node.rotational_velocity * (1 - dt) if glm.length2(node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)

while engine.running:
    
    looked = actions(looked)
    
    update_node(engine.delta_time)
    
    scene.update()
    engine.update()

