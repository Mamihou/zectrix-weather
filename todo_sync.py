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
    
    url = "https://api.todoist.com/rest/v2/tasks"
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    print("请求Todoist API获取待办事项")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Todoist API响应状态码: {response.status_code}")
        if response.status_code == 200:
            return response.json()
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
            return data.get("data", [])
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
    
    url = f"https://api.todoist.com/rest/v2/tasks/{task_id}"
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

def push_todos_to_device():
    """推送待办事项到设备显示"""
    todos = get_zectrix_todos()
    
    # 获取中国时区（UTC+8）的当前时间
    china_tz = timezone(timedelta(hours=8))
    current_time = datetime.now(china_tz).strftime("%Y-%m-%d %H:%M")
    
    # 构建待办事项的文本
    todo_text = f"上一次同步时间: {current_time}\n{'=' * 61}\n　　　　　　　　　待办事项\n\n"
    
    # 过滤未完成的任务并按优先级排序
    active_todos = [t for t in todos if not t.get('completed', False)]
    # 按优先级排序（priority: 1=低, 2=中, 3=高, 4=最高）
    active_todos.sort(key=lambda x: x.get('priority', 1), reverse=True)
    
    if active_todos:
        for i, todo in enumerate(active_todos[:10]):  # 只显示前10个
            content = todo.get('content', '无内容')
            priority = todo.get('priority', 1)
            status = "✓" if todo.get('completed', False) else "□"
            
            # 优先级标记
            priority_marks = {
                1: "  ",  # 低优先级
                2: "! ",  # 中优先级
                3: "!!",  # 高优先级
                4: "!!!"  # 最高优先级
            }
            priority_mark = priority_marks.get(priority, "  ")
            
            todo_text += f"{i+1:>2}. {status} {priority_mark} {content}\n"
    else:
        todo_text += "当前没有待办事项\n"
    
    # 推送到第2页
    push_to_device(todo_text, "2")
    
    return {"code": 0, "message": "成功推送待办事项到第2页"}

def push_to_device(text, page_id):
    """推送内容到设备的指定页面"""
    if not DEVICE_ID:
        print("错误: 设备ID未设置")
        return
    
    url = f"https://cloud.zectrix.com/open/v1/devices/{DEVICE_ID}/display/text"
    headers = {
        "X-API-Key": ZECTRIX_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "fontSize": 11,
        "pageId": page_id
    }
    print(f"推送页面 {page_id} 到设备 {DEVICE_ID}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"推送响应: {response.status_code} - {response.text}")
        return response.json()
    except Exception as e:
        print(f"推送异常: {str(e)}")
        return {"code": 500, "message": str(e)}

if __name__ == "__main__":
    print(f"设备ID: {DEVICE_ID}")
    
    # 双向同步待办事项
    print("\n=== 双向同步待办事项 ===")
    print("1. 同步Todoist到设备")
    sync_todoist_to_zectrix()
    print("2. 同步设备到Todoist")
    sync_zectrix_to_todoist()
    
    # 推送待办事项到设备显示
    print("\n=== 推送待办事项到设备显示 ===")
    todo_result = push_todos_to_device()
    print("待办事项推送结果:", todo_result)
    
    print("\n总推送结果:", {"todo": todo_result})
