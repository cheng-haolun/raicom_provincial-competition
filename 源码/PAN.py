#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import rospy
import tf
import actionlib
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal,MoveBaseActionResult,MoveBaseActionGoal
from std_srvs.srv  import    *
from actionlib import SimpleActionClient
from re import sub

client=None

emergency_stop = False#紧急停止状态标志变量

#初始化模块
def init():
    global client
    client = SimpleActionClient('move_base', MoveBaseAction)#打开move_base节点
    #连接动作服务器
    rospy.loginfo("等待move_base动作服务器...")
    client.wait_for_server()
    rospy.loginfo("已连接到move_base动作服务器")

#获取初始化点位数据
def data_init(path):
    try:
        goals={}
        key_list=[]
        with open(path) as file:
            for line in file:
                #遇到‘#’跳过该点
                if '#' in line:
                    continue
                #遇到‘！’停止读取
                elif '!' in line:
                    break
                #正常读取
                else:
                    key,value=line.strip().split(':',1)
                    points=value.split(',')
                    group_goals = []
                    group_goals.append([float(points[0]), float(points[1]), float(points[2]), float(points[3])])
                    goals[key]=group_goals
                    key_list.append(key)
        return goals,key_list
    #报错处理
    except Exception as e:
        rospy.logerr("读取目标点文件失败: %s" % e)
        return {}, []

#导航模块
def navigate_to_point(x, y, z, w):
    global client
    try:
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"#获取地图
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x#获取x坐标
        goal.target_pose.pose.position.y = y#获取y坐标
        goal.target_pose.pose.orientation.z = z#获取z坐标
        goal.target_pose.pose.orientation.w = w#获取w坐标
        client.send_goal(goal)#导航至点
        rospy.loginfo("导航到目标: x=%.2f, y=%.2f, z=%.2f, w=%.2f" % (x, y, z, w))
        rospy.loginfo("导航成功")
        result = client.wait_for_result()#获取导航结果
        #结果判定
        if result:
            rospy.loginfo("导航完成！")
        else:
            rospy.logerr("导航失败！")
        return result
    except Exception,e:
        rospy.logerr("导航失败: %s" % e)
        return None
    except rospy.ROSException,e:
        rospy.logerr("ros错误: %s" % e)
        return None
#紧急停止判定模块
def emergency_stop_callback(msg):
    global emergency_stop
    emergency_stop = True
    rospy.loginfo("收到紧急停止信号!")

#主函数模块
def main():
    data_path='/home/mowen/DHHTV4.2/datadh.txt'#数据路径
    rospy.init_node('move_base_node')#初始化启动节点
    rospy.Subscriber('emergency_stop', Empty, emergency_stop_callback)#启动紧急停止节点
    init()#初始化
    our_goals,key_list=data_init(data_path)#获取点位数据
    #导航模块
    for group_name in key_list:
        if rospy.is_shutdown() or emergency_stop:
            rospy.loginfo("紧急中断程序！")
            rospy.loginfo("中断的点为：%s" % re.sub(r'\*', ' ', group_name))
            break
        goals=our_goals[group_name]
        rospy.loginfo("处理组: %s" % sub(r'\*',' ',group_name))
        for goal in goals:
            rospy.loginfo("导航到新的目标位置...")
            result = navigate_to_point(*goal)
            if not result:
                rospy.logerr("导航失败，跳过下面的点")
                break

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation interrupted.")
    pass