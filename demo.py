#!/usr/bin/env python3

from BlazeposeRenderer import BlazeposeRenderer
import argparse
import gripper_fcn as gf
import Util as util

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--edge', action="store_true",
                    help="Use Edge mode (postprocessing runs on the device)")
parser_tracker = parser.add_argument_group("Tracker arguments")                 
parser_tracker.add_argument('-i', '--input', type=str, default="rgb", 
                    help="'rgb' or 'rgb_laconic' or path to video/image file to use as input (default=%(default)s)")
parser_tracker.add_argument("--pd_m", type=str,
                    help="Path to an .blob file for pose detection model")
parser_tracker.add_argument("--lm_m", type=str,
                    help="Landmark model ('full' or 'lite' or 'heavy') or path to an .blob file")
parser_tracker.add_argument('-xyz', '--xyz', action="store_true", 
                    help="Get (x,y,z) coords of reference body keypoint in camera coord system (only for compatible devices)")
parser_tracker.add_argument('-c', '--crop', action="store_true", 
                    help="Center crop frames to a square shape before feeding pose detection model")
parser_tracker.add_argument('--no_smoothing', action="store_true", 
                    help="Disable smoothing filter")
parser_tracker.add_argument('-f', '--internal_fps', type=int, 
                    help="Fps of internal color camera. Too high value lower NN fps (default= depends on the model)")                    
parser_tracker.add_argument('--internal_frame_height', type=int, default=640,                                                                                    
                    help="Internal color camera frame height in pixels (default=%(default)i)")                    
parser_tracker.add_argument('-s', '--stats', action="store_true", 
                    help="Print some statistics at exit")
parser_tracker.add_argument('-t', '--trace', action="store_true", 
                    help="Print some debug messages")
parser_tracker.add_argument('--force_detection', action="store_true", 
                    help="Force person detection on every frame (never use landmarks from previous frame to determine ROI)")

parser_renderer = parser.add_argument_group("Renderer arguments")
parser_renderer.add_argument('-3', '--show_3d', choices=[None, "image", "world", "mixed"], default=None,
                    help="Display skeleton in 3d in a separate window. See README for description.")
parser_renderer.add_argument("-o","--output",
                    help="Path to output video file")
 

args = parser.parse_args()

if args.edge:
    from BlazeposeDepthaiEdge import BlazeposeDepthai
else:
    from BlazeposeDepthai import BlazeposeDepthai
tracker = BlazeposeDepthai(input_src=args.input, 
            pd_model=args.pd_m,
            lm_model=args.lm_m,
            smoothing=not args.no_smoothing,   
            # xyz=args.xyz,            
            xyz=True,            
            crop=args.crop,
            internal_fps=args.internal_fps,
            internal_frame_height=args.internal_frame_height,
            force_detection=args.force_detection,
            stats=True,
            trace=args.trace)   

grip = gf.RobotiqGripper("/dev/ttyUSB1")

renderer = BlazeposeRenderer(
                tracker, 
                show_3d=args.show_3d, 
                output=args.output)

is_hand_gripping = False
hand_pause_time = 0
start_time = None

while True:
    # Run blazepose on next frame
    frame, body = tracker.next_frame()

    # Test: get xyz in camera space
    # left_heel_xyz = tracker.query_landmark_xyz(body, 27)
    # if (left_heel_xyz[0] > 400 and left_heel_xyz[1] < 366):
    #     print("a person in forbidden zone!!! stop the robot!!!")
    # print(left_heel_xyz)
    if body is not None:
        left_hand_pixel = body.landmarks[19]
        right_hand_pixel = body.landmarks[20]
        
        if (right_hand_pixel[0] > 250 and right_hand_pixel[0] < 313 and right_hand_pixel[1] > 200 and right_hand_pixel[1] < 260):
            if is_hand_gripping == False:
                start_time = util.now()
            if (util.now() - start_time > 2):
                util.open_gripper(grip)
            is_hand_gripping = True
        else:
            is_hand_gripping = False
        #     if hand_pause_time > 2:
        #         util.open_gripper(grip)
        #     if start_time is not None and is_hand_gripping == True:
        #         hand_pause_time += util.now() - start_time
        #     is_hand_gripping = True
        # else:
        #     is_hand_gripping = False
        #     hand_pause_time = 0
         
    # start_time = util.now()
    if frame is None: break
    # Draw 2d skeleton
    frame = renderer.draw(frame, body)
    key = renderer.waitKey(delay=1)
    if key == 27 or key == ord('q'):
        break
renderer.exit()
tracker.exit()