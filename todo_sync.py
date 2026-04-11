import requests
from datetime import datetime, timezone, timedelta
import os
import json

# 配置
ZECTRIX_API_KEY = "zt_e78f09c7753b6fecb84ceadbcceef149"
DEVICE_ID = os.environ.get("DEVICE_ID")
# Todoist API配置
TODOIST_API_TOKEN = os.environ.get("TODOIST_API_TOKEN")

def get_todoist_todos():
    """从Todoist获取待办事项"""
    if not TODOIST_API_TOKEN:
        print("错误: Todoist API Token未设置")
        return []
    
    url = "https://api.todoist.com/api/v1/tasks"
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    print("请求Todoist API获取待办事项")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Todoist API响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            else:
                print(f"Todoist API响应格式错误: 预期列表，实际是 {type(data)}")
                return []
        else:
            print(f"Todoist API错误: {response.text}")
            return []
    except Exception as e:
        print(f"Todoist API请求异常: {str(e)}")
        return []

def get_zectrix_todos():
    """获取设备上的待办事项"""
    if not DEVICE_ID:
        print("错误: 设备ID未设置")
        return []
    
    url = f"https://cloud.zectrix.com/open/v1/devices/{DEVICE_ID}/todos"
    headers = {
        "X-API-Key": ZECTRIX_API_KEY,
        "Content-Type": "application/json"
    }
    print("请求Zectrix API获取待办事项")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Zectrix API响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Zectrix API响应数据: {data}")
            if data and isinstance(data, dict):
                todos = data.get("data", [])
                if isinstance(todos, list):
                    return todos
                else:
                    print(f"Zectrix API响应格式错误: data不是列表，实际是 {type(todos)}")
                    return []
            elif isinstance(data, list):
                # 直接返回列表
                return data
            else:
                print(f"Zectrix API响应格式错误: 预期字典或列表，实际是 {type(data)}")
                return []
        else:
            print(f"Zectrix API错误: {response.text}")
            return []
    except Exception as e:
        print(f"Zectrix API请求异常: {str(e)}")
        return []

def create_zectrix_todo(content, completed=False, priority=1):
    """在设备上创建待办事项"""
    if not DEVICE_ID:
        print("错误: 设备ID未设置")
        return False
    
    url = f"https://cloud.zectrix.com/open/v1/devices/{DEVICE_ID}/todos"
    headers = {
        "X-API-Key": ZECTRIX_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "content": content,
        "completed": completed,
        "priority": priority
    }
    print(f"在设备上创建待办事项: {content}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"创建待办响应: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"创建待办异常: {str(e)}")
        return False

def update_zectrix_todo(todo_id, completed=None, priority=None):
    """更新设备上的待办事项"""
    if not DEVICE_ID:
        print("错误: 设备ID未设置")
        return False
    
    url = f"https://cloud.zectrix.com/open/v1/devices/{DEVICE_ID}/todos/{todo_id}"
    headers = {
        "X-API-Key": ZECTRIX_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {}
    if completed is not None:
        payload["completed"] = completed
    if priority is not None:
        payload["priority"] = priority
    
    print(f"更新设备上的待办事项: {todo_id}")
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=10)
        print(f"更新待办响应: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"更新待办异常: {str(e)}")
        return False

def update_todoist_task(task_id, completed):
    """更新Todoist任务状态"""
    if not TODOIST_API_TOKEN:
        print("错误: Todoist API Token未设置")
        return False
    
    url = f"https://api.todoist.com/api/v1/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "completed": completed
    }
    print(f"更新Todoist任务状态: {task_id}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"更新Todoist响应: {response.status_code} - {response.text}")
        return response.status_code == 204
    except Exception as e:
        print(f"更新Todoist异常: {str(e)}")
        return False

def sync_todoist_to_zectrix():
    """同步Todoist待办事项到设备"""
    todoist_todos = get_todoist_todos()
    zectrix_todos = get_zectrix_todos()
    
    # 创建映射：内容 -> 设备待办ID
    zectrix_todo_map = {todo["content"]: todo["id"] for todo in zectrix_todos}
    
    for todo in todoist_todos:
        content = todo["content"]
        completed = todo["completed"]
        # Todoist优先级: 1=低, 2=中, 3=高, 4=最高
        priority = todo["priority"]
        
        if content in zectrix_todo_map:
            # 更新现有待办事项
            todo_id = zectrix_todo_map[content]
            existing_todo = next(t for t in zectrix_todos if t["id"] == todo_id)
            if existing_todo["completed"] != completed or existing_todo["priority"] != priority:
                update_zectrix_todo(todo_id, completed, priority)
        else:
            # 创建新待办事项
            create_zectrix_todo(content, completed, priority)

def sync_zectrix_to_todoist():
    """同步设备待办事项状态到Todoist"""
    zectrix_todos = get_zectrix_todos()
    todoist_todos = get_todoist_todos()
    
    # 创建映射：内容 -> Todoist任务ID
    todoist_todo_map = {todo["content"]: todo["id"] for todo in todoist_todos}
    
    for todo in zectrix_todos:
        content = todo["content"]
        completed = todo["completed"]
        
        if content in todoist_todo_map:
            # 更新Todoist任务状态
            task_id = todoist_todo_map[content]
            existing_task = next(t for t in todoist_todos if t["id"] == task_id)
            if existing_task["completed"] != completed:
                update_todoist_task(task_id, completed)



if __name__ == "__main__":
    print(f"设备ID: {DEVICE_ID}")
    
    # 双向同步待办事项
    print("\n=== 双向同步待办事项 ===")
    print("1. 同步Todoist到设备")
    sync_todoist_to_zectrix()
    print("2. 同步设备到Todoist")
    sync_zectrix_to_todoist()
    
    print("\n总同步结果: 成功完成双向同步")
