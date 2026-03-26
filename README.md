# Asher Robot - Holonomic Teleoperation & Mapping
## Overview
This package adds holonomic (omnidirectional) drive capability to the Asher robot platform.
It includes:
- 4-wheel mecanum drive URDF for simulation (`box_bot_holonomic.urdf`)
- Asher's actual URDF with 4 wheels added (`URDF_simp6_holonomic.urdf`)
- Custom holonomic teleop node (`asher_teleop`)
- Front and rear 2D lidar sensors

## What Changed From Original box_bot
| Original | Holonomic Version |
|---|---|
| 2 wheels + caster | 4 mecanum wheels |
| diff_drive plugin | planar_move plugin |
| linear.x and angular.z only | linear.x, linear.y, angular.z |
| Cannot strafe | Can strafe left/right |
| No lidar | Front + rear 2D lidar |

---

## Requirements
- Docker Desktop
- VcXsrv (for display on Windows)
- The `uyiosaamadasun/ros_humble_x86_64:latest` Docker image

---

## Setup - Every Time You Start

### Step 1 - Start XLaunch (Windows display server)
- Search "XLaunch" in Start menu
- Settings: Multiple windows → Start no client → Check "Disable access control" → Finish

### Step 2 - Start Docker container (PowerShell Tab 1)
```bash
docker run -it --rm --privileged --network host --ipc host --runtime nvidia \
  -v ~/.:/docs -v C:\ros2_ws:/ros2_ws \
  --name robot_software_v3 \
  uyiosaamadasun/ros_humble_x86_64:latest /bin/bash
```

### Step 3 - Launch Gazebo (inside container)
```bash
export DISPLAY=host.docker.internal:0.0
source /opt/ros/humble/setup.bash
ros2 launch gazebo_ros gazebo.launch.py
```

### Step 4 - Load robot URDF (new tab)
```bash
docker exec -it robot_software_v3 /bin/bash
source /opt/ros/humble/setup.bash
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -p robot_description:="$(cat /ros2_ws/src/asher_navigation/box_bot_holonomic.urdf)" \
  -p use_sim_time:=true
```

### Step 5 - Spawn robot in Gazebo (new tab)
```bash
docker exec -it robot_software_v3 /bin/bash
source /opt/ros/humble/setup.bash
ros2 run gazebo_ros spawn_entity.py \
  -topic robot_description -entity robot -x 0 -y 0 -z 0.5
```

### Step 6 - Run teleop (new tab)
```bash
docker exec -it robot_software_v3 /bin/bash
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash
ros2 run asher_teleop teleop_keyboard
```

---

## Teleop Key Bindings
| Key | Action |
|-----|--------|
| w | Forward |
| s | Backward |
| a | Strafe left |
| d | Strafe right |
| q | Rotate left |
| e | Rotate right |
| Space | Stop |
| Ctrl-C | Quit |

---

## Running RTAB-Map (Mapping)
```bash
docker exec -it robot_software_v3 /bin/bash
source /opt/ros/humble/setup.bash
ros2 launch rtabmap_launch rtabmap.launch.py \
    rtabmap_args:="--delete_db_on_start" \
    depth_topic:=/depth_camera/depth/image_raw \
    rgb_topic:=/depth_camera/image_raw \
    camera_info_topic:=/depth_camera/depth/camera_info \
    frame_id:=base_link \
    approx_sync:=true \
    visual_odometry:=false \
    odom_topic:=/odom \
    use_sim_time:=true \
    rviz:=true
```
Then drive the robot around with teleop to build the map.

---

## Running RTAB-Map (Navigation with existing map)
```bash
ros2 launch rtabmap_launch rtabmap.launch.py \
    localization:=true \
    database_path:=/path/to/my_map.db \
    depth_topic:=/depth_camera/depth/image_raw \
    rgb_topic:=/depth_camera/image_raw \
    camera_info_topic:=/depth_camera/depth/camera_info \
    frame_id:=base_link \
    approx_sync:=true \
    visual_odometry:=false \
    odom_topic:=/odom \
    rviz:=true
```

---

## Sensor Topics
| Topic | Type | Description |
|-------|------|-------------|
| /cmd_vel | geometry_msgs/Twist | Velocity commands |
| /odom | nav_msgs/Odometry | Robot odometry |
| /depth_camera/image_raw | sensor_msgs/Image | RGB camera |
| /depth_camera/depth/image_raw | sensor_msgs/Image | Depth camera |
| /front_scan | sensor_msgs/LaserScan | Front 2D lidar |
| /rear_scan | sensor_msgs/LaserScan | Rear 2D lidar |

---

## File Structure
```
ros2_ws/src/
├── asher_navigation/
│   ├── box_bot_holonomic.urdf     ← simulation robot (4 wheels + lidars)
│   ├── URDF_simp6_holonomic.urdf  ← Asher's actual URDF (4 wheels)
│   ├── box_bot_ros2_fixed.urdf    ← original 2-wheel robot (reference)
│   ├── my_world.sdf               ← Gazebo world
│   └── goal_relay.py              ← Nav2 goal relay
└── asher_teleop/
    ├── asher_teleop/
    │   └── teleop_keyboard.py     ← holonomic teleop node
    ├── package.xml
    └── setup.py
```

---

## Troubleshooting
**Gazebo won't open:**
Make sure XLaunch is running and run `export DISPLAY=host.docker.internal:0.0` before launching.

**Container name conflict:**
```bash
docker rm robot_software_v3
```
Then start again.

**Teleop not found:**
```bash
cd /ros2_ws
colcon build --packages-select asher_teleop --symlink-install
source install/setup.bash
```

**Robot not moving:**
Check `/cmd_vel` is publishing: `ros2 topic echo /cmd_vel`
