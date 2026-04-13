import pygame
import math
import subprocess
import threading
import time
import re
import random

# Print ASCII text "WIFI SCAN" in green
ascii_art = "\033[92m" + r"""
 __          __  _____  ______  _____    _____   _____          _   _ 
 \ \        / / |_   _||  ____||_   _|  / ____| / ____|   /\   | \ | |
  \ \  /\  / /    | |  | |__     | |   | (___  | |       /  \  |  \| |
   \ \/  \/ /     | |  |  __|    | |    \___ \ | |      / /\ \ | . ` |
    \  /\  /     _| |_ | |      _| |_   ____) || |____ / ____ \| |\  |
     \/  \/     |_____||_|     |_____| |_____/  \_____/_/    \_\_| \_|

        [ WIFI SCAN was developed by Khanh in 2007 ]
""" + "\033[0m"
print(ascii_art)

# Initialize pygame
pygame.init()

# Setup display
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wi-Fi Radar Scanner")

# Colors
BLACK = (0, 0, 0)
DARK_GREEN = (0, 50, 0)
LIGHT_GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
TEXT_COLOR = (0, 200, 0)

# Fonts
font = pygame.font.SysFont("consolas", 14)
large_font = pygame.font.SysFont("consolas", 22, bold=True)

# Radar settings
CENTER = (WIDTH // 2, HEIGHT // 2)
MAX_RADIUS = 350
SPEED = 0.03 # Sweeping speed

# Data structure for networks
# SSID -> {'ssid': str, 'signal': int, 'angle': float, 'alpha': int}
networks = {}

def scan_wifi():
    global networks
    while True:
        try:
            # Run the command to get wifi networks
            # We don't use text=True to handle possible encoding issues safely
            result = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            output = result.stdout.decode('utf-8', errors='replace')
            
            # Parse output
            current_networks = {}
            current_ssid = ""
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith("SSID"):
                    # Extract SSID name
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_ssid = parts[1].strip()
                        if current_ssid == "":
                            current_ssid = "Hidden Network"
                elif line.startswith("Signal"):
                    # Extract signal percentage
                    signal_match = re.search(r"(\d+)%", line)
                    if signal_match and current_ssid:
                        signal_strength = int(signal_match.group(1))
                        # Keep the strongest signal if multiple BSSIDs exist for one SSID
                        if current_ssid not in current_networks or signal_strength > current_networks[current_ssid]:
                            current_networks[current_ssid] = signal_strength
            
            # Update global list
            for ssid, signal in current_networks.items():
                if ssid not in networks:
                    networks[ssid] = {
                        'ssid': ssid,
                        'signal': signal,
                        'angle': random.uniform(0, 2 * math.pi),
                        'alpha': 255
                    }
                else:
                    networks[ssid]['signal'] = signal
                    # alpha will be updated by radar sweep instead of randomly brightening
                    # networks[ssid]['alpha'] = 255
                    
            # Set networks that are no longer present to fade out completely or just remove them
            # For radar effect, it's cool if they persist a little but eventually disappear if strictly wanted
            # For now, let's just keep them updated.

        except Exception as e:
            print(f"Error scanning wifi: {e}")
            
        time.sleep(4) # Scan every 4 seconds

# Start background thread for scanning
scan_thread = threading.Thread(target=scan_wifi, daemon=True)
scan_thread.start()

# Main loop
running = True
angle = 0
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen with black
    screen.fill(BLACK)

    # Draw radar grid (concentric circles)
    for r in range(50, MAX_RADIUS + 1, 50):
        pygame.draw.circle(screen, DARK_GREEN, CENTER, r, 1)

    # Draw crosshairs
    pygame.draw.line(screen, DARK_GREEN, (CENTER[0], CENTER[1] - MAX_RADIUS), (CENTER[0], CENTER[1] + MAX_RADIUS), 1)
    pygame.draw.line(screen, DARK_GREEN, (CENTER[0] - MAX_RADIUS, CENTER[1]), (CENTER[0] + MAX_RADIUS, CENTER[1]), 1)

    # Calculate sweep line end point
    end_x = CENTER[0] + MAX_RADIUS * math.cos(angle)
    end_y = CENTER[1] + MAX_RADIUS * math.sin(angle)

    # Draw sweeper trail (polygon for a cool gradient effect)
    trail_length = 40
    for i in range(trail_length):
        trail_angle = angle - (i * 0.02)
        t_end_x = CENTER[0] + MAX_RADIUS * math.cos(trail_angle)
        t_end_y = CENTER[1] + MAX_RADIUS * math.sin(trail_angle)
        
        # Calculate trailing color intensity
        color_intensity = max(0, 255 - (i * (255 // trail_length)))
        trail_color = (0, color_intensity, 0)
        pygame.draw.line(screen, trail_color, CENTER, (t_end_x, t_end_y), 2)

    # Draw main scan line
    pygame.draw.line(screen, LIGHT_GREEN, CENTER, (end_x, end_y), 2)

    # Process and draw networks (blips)
    current_sweep_angle = angle % (2 * math.pi)
    
    for ssid, data in networks.items():
        signal = data['signal']
        net_angle = data['angle']
        
        # Map signal strength to distance from center 
        # Stronger signal (100%) = closer to center (50px)
        # Weaker signal (0%) = further from center (MAX_RADIUS)
        distance = MAX_RADIUS - ((signal / 100.0) * (MAX_RADIUS - 50))
        
        nx = CENTER[0] + distance * math.cos(net_angle)
        ny = CENTER[1] + distance * math.sin(net_angle)
        
        # Normalize the network angle
        norm_net_angle = net_angle % (2 * math.pi)
        
        # Check if sweep line just passed the blip
        angle_diff = current_sweep_angle - norm_net_angle
        # Fix wrap-around difference
        if angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        elif angle_diff > math.pi:
            angle_diff -= 2 * math.pi
            
        if 0 <= angle_diff <= SPEED * 2:
            data['alpha'] = 255 # Brighten when scanned
            
        # Decrease alpha for fading effect
        alpha = data['alpha']
        data['alpha'] = max(40, alpha - 3) # minimum brightness 40 so it doesn't vanish entirely
            
        # Draw blip and text if visible
        if alpha > 0:
            # Use alpha blending for the dot
            blip_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            
            # Outer glow
            pygame.draw.circle(blip_surf, (0, 255, 0, alpha // 3), (10, 10), 8)
            # Inner core
            pygame.draw.circle(blip_surf, (0, 255, 0, alpha), (10, 10), 3)
            
            screen.blit(blip_surf, (nx - 10, ny - 10))
            
            # Only draw text if recently swept or decently bright
            if alpha > 100:
                text_surf = font.render(f"{ssid} ({signal}%)", True, (0, alpha, 0))
                screen.blit(text_surf, (nx + 12, ny - 8))
            
    # Update UI text
    title_text = large_font.render("WIFI RADAR SCANNER", True, LIGHT_GREEN)
    screen.blit(title_text, (20, 20))
    
    count_text = font.render(f"Targets Acquired: {len(networks)}", True, TEXT_COLOR)
    screen.blit(count_text, (20, 50))
    
    status_text = font.render("Scanning Background Activity... Active", True, TEXT_COLOR)
    screen.blit(status_text, (20, 70))

    # Increment angle for sweeping motion
    angle += SPEED
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
