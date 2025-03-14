import threading
import random
import time
import socket

class Message:
    def __init__(self, sender_id, timestamp, content):
        self.sender_id = sender_id
        self.timestamp = timestamp.copy()  # Prevent aliasing
        self.content = content

    def __repr__(self):
        return f"Message(sender={self.sender_id}, timestamp={self.timestamp}, content='{self.content}')"

class Process:
    def __init__(self, pid, ip, port):
        self.id = pid
        self.ip = ip  # Store IP address
        self.port = port  # Store Port number
        self.vector_clock = {}  
        self.pending_messages = []
        self.delivered_messages = []
        self.network = None
        self.ready_to_send = False  # Prevent sending until five nodes join

    def join_network(self, network):
        self.network = network
        network.add_process(self)
        # Initialize vector clock with current network member IDs
        self.initialize_vector_clock(network.get_member_ids())
        self.start_periodic_check()

    def initialize_vector_clock(self, member_ids):
        self.vector_clock = {pid: 0 for pid in member_ids}

    def update_vector_clock_for_new_member(self, new_pid):
        if new_pid not in self.vector_clock:
            self.vector_clock[new_pid] = 0

    def remove_member_from_vector_clock(self, pid):
        if pid in self.vector_clock:
            del self.vector_clock[pid]

    def start_periodic_check(self, interval=1.0):
        """Periodically recheck pending messages for delivery."""
        def check():
            self.try_deliver_messages()
            timer = threading.Timer(interval, check)
            timer.daemon = True
            timer.start()
        check()

    def send_message(self, content):
        if self.network is None:
            print(f"[Process {self.id}] Not connected to a network.")
            return
        if not self.ready_to_send:
            print(f"[Process {self.id}] Cannot send message. Waiting for 5 nodes to join.")
            return
        self.vector_clock[self.id] += 1
        timestamp = self.vector_clock.copy()
        message = Message(self.id, timestamp, content)
        print(f"[Process {self.id}] Sending message '{content}' with timestamp {timestamp}")
        self.network.multicast(self, message)


    def receive_message(self, message):
        print(f"[Process {self.id}] Received message '{message.content}' from {message.sender_id} (timestamp: {message.timestamp})")
        self.pending_messages.append(message)
        self.try_deliver_messages()

    def can_deliver(self, message):
        sender_id = message.sender_id
        # Condition 1: The message is the next expected from the sender
        expected = self.vector_clock[sender_id] + 1
        if message.timestamp[sender_id] != expected:
            print(f"[Process {self.id}] Cannot deliver '{message.content}': Expected seq {expected} from {sender_id}, got {message.timestamp[sender_id]}")
            return False
        # Condition 2: All other entries in the timestamp are ≤ current vector clock
        for pid, ts in message.timestamp.items():
            if pid != sender_id and ts > self.vector_clock.get(pid, 0):
                print(f"[Process {self.id}] Cannot deliver '{message.content}': Process {pid} has VC {self.vector_clock.get(pid, 0)}, message requires ≤ {ts}")
                return False
        return True

    def deliver(self, message):
        print(f"[Process {self.id}] Delivering message '{message.content}' from {message.sender_id}")
        # Update vector clock entry-wise to the maximum of current and message's timestamp
        for pid in self.vector_clock:
            self.vector_clock[pid] = max(self.vector_clock[pid], message.timestamp.get(pid, 0))
        self.delivered_messages.append(message)
        print(f"[Process {self.id}] Updated vector clock: {self.vector_clock}\n")

    def try_deliver_messages(self):
        delivered_any = True
        while delivered_any:
            delivered_any = False
            for msg in list(self.pending_messages):
                if self.can_deliver(msg):
                    self.deliver(msg)
                    self.pending_messages.remove(msg)
                    delivered_any = True
                    break  # Restart loop after a successful delivery

class Network:
    def __init__(self):
        self.processes = []
        self.bootstrap_node = None

    def add_process(self, process):
        if not self.processes:  # First node to join becomes bootstrap
            self.bootstrap_node = process
            print(f"[Network] Process {process.id} is the bootstrap node.")

        self.processes.append(process)
        
        # Update vector clocks for all processes
        for proc in self.processes:
            proc.update_vector_clock_for_new_member(process.id)

        # If exactly five nodes joined, notify all
        if len(self.processes) == 5:
            self.notify_all_nodes_ready()

    def notify_all_nodes_ready(self):
        print("[Network] All five nodes have joined. Message sending is now allowed.")
        for proc in self.processes:
            proc.ready_to_send = True  # Let processes know they can now send messages
            
    def remove_process(self, process):
        if process in self.processes:
            self.processes.remove(process)
            for proc in self.processes:
                proc.remove_member_from_vector_clock(process.id)

    def get_member_ids(self):
        return [proc.id for proc in self.processes]

    def multicast(self, sender, message, recipient_delays=None):
        """
        Explicit multicast: send message to all processes except the sender.
        recipient_delays (optional) is a dict mapping process IDs to a fixed delay (in seconds)
        to facilitate testing of out-of-order delivery.
        """
        for proc in self.processes:
            if proc.id != sender.id:
                # Choose a delay: use provided delay or a random delay between 0.1s and 1.0s
                delay = recipient_delays.get(proc.id, random.uniform(0.1, 1.0)) if recipient_delays else random.uniform(0.1, 1.0)
                print(f"[Network] Scheduling delivery of message '{message.content}' from {message.sender_id} to Process {proc.id} after {delay:.2f}s delay")
                timer = threading.Timer(delay, proc.receive_message, args=(message,))
                timer.daemon = True
                timer.start()

def main():
    network = Network()
    local_ip = socket.gethostbyname(socket.gethostname())
    # Create processes and have them join the network
    p1 = Process(1, local_ip, 5001)
    p2 = Process(2, local_ip, 5002)
    p3 = Process(3, local_ip, 5003)
    p4 = Process(4, local_ip, 5004)
    p5 = Process(5, local_ip, 5005)
    p1.join_network(network)
    p2.join_network(network)
    p3.join_network(network)
    p4.join_network(network)
    p5.join_network(network)

    # Simulate sending messages with network delay.
    # P1 sends message 'm'
    p1.send_message("m")
    # Allow some time for deliveries
    time.sleep(2)

    # P2 sends message 'm+' after receiving 'm'
    p2.send_message("m+")
    time.sleep(2)

    # P1 sends another message 'm++'
    p1.send_message("m++")
    time.sleep(2)

    # Simulate removal: remove p2 from the network.
    network.remove_process(p2)
    print("[Network] Process 2 removed from the network.\n")
    # P3 sends a message 'hello'
    p3.send_message("hello")
    time.sleep(2)

if __name__ == "__main__":
    main()
