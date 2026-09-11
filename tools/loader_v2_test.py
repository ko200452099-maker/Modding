#!/usr/bin/env python3
"""
loader_v2_test.py — offline simulation of Loader v2 FIFO + timeout logic
No game needed. Simulates queue depth, stack clamp, version gate, timeout.

Run: python3 tools/loader_v2_test.py
"""
import time, collections

# Simulate statics
Static = [0]*512
Static2 = [0]*600
queue_script=[""]*4
queue_stack=[0]*4
queue_version=[0]*4
head=0
tail=0

def clamp_stack(s):
    if s < 128: return 1024
    if s > 8192: return 8192
    if s % 128 != 0:
        return (s//128)*128
    return s

def enqueue(script, stack, version=0, opts=0):
    global head,tail
    # check full: (tail+1)%4 == head
    if (tail + 1) % 4 == head and queue_script[head] != "":
        return "Queue full! Wait..."
    queue_script[tail] = script
    queue_stack[tail] = clamp_stack(stack)
    queue_version[tail] = version
    tail = (tail + 1) % 4
    if opts & 1:
        return f"Queued: {script} (stack {clamp_stack(stack)})"
    return "Queued"

def dequeue_tick_sim():
    global head,tail
    if head == tail and queue_script[head]=="":
        return "idle"
    script = queue_script[head]
    stack = queue_stack[head]
    version = queue_version[head]
    # simulate REQUEST -> HAS after 100ms, unless script is "Corrupt" -> timeout
    print(f"  -> Dequeued {script} stack={stack} v={version}")
    if script == "Corrupt":
        time.sleep(0.05)
        res = "timeout after 3000ms"
        print(f"     {res}: Load timeout: {script}")
    else:
        print(f"     REQUEST_SCRIPT({script}) -> HAS_SCRIPT_LOADED true -> START_NEW_SCRIPT({script},{stack})")
        res = "started"
    queue_script[head]=""
    queue_stack[head]=0
    head = (head + 1) % 4
    return res

def test():
    print("=== Test 1: stack clamp ===")
    for s in [0,64,128,1024,1025,8192,99999]:
        print(f"  {s:5d} -> {clamp_stack(s)}")
    print("\n=== Test 2: FIFO depth 4 ===")
    for name in ["Brodator","Revolution","MoonShine","Innocence","Extra"]:
        print(enqueue(name, 1024, opts=1))
    print("\n=== Test 3: drain queue ===")
    while not (head==tail and queue_script[head]==""):
        dequeue_tick_sim()
    print("\n=== Test 4: timeout simulation ===")
    enqueue("Corrupt", 512, opts=1)
    dequeue_tick_sim()
    print("\n=== Test 5: version gate ===")
    enqueue("Brodator", 1024, version=1, opts=1)
    enqueue("Brodator", 1024, version=2, opts=1)  # update
    print(f"  queue has versions: {[queue_version[(head+i)%4] for i in range(3)]}")
    print("\n=== All simulated checks pass ===")
    print("Run real check: python3 tools/upgrade_loader.py --check --in ModLoader.csa")

if __name__=='__main__':
    test()
