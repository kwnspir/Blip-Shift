import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import random
import math
from matplotlib.animation import FuncAnimation

# Default Parameters
RPM_1 = 13.5  # First RPM option
RPM_2 = 27.0  # Second RPM option
TARGET_MOVE_MULTIPLIER = 0.1  # Multiplier to control how much the target moves once it's reset

# Setup the Tkinter window
class RadarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radar PPI Screen")

        # Initialize RPM
        self.rpm = RPM_1  # Start with the first RPM value
        self.sweep_speed = self.calculate_sweep_speed()

        # Setup the Radar Display
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6, 6))
        self.ax.set_ylim(0, 100)
        self.ax.set_xticks(np.linspace(0, 2 * np.pi, 8, endpoint=False))  # Set ticks at 0, 45, 90... degrees
        self.ax.set_yticklabels([])
        self.ax.set_theta_zero_location('N')  # 0 degrees at top
        self.ax.set_theta_direction(-1)  # Clockwise

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Radar sweep line
        self.sweep_line, = self.ax.plot([], [], color='green', lw=2)

        # Fake targets (angle in radians, distance, fade alpha)
        self.targets = self.generate_fake_targets(10)

        # Target markers
        self.target_plots = [self.ax.plot([], [], 'ro', alpha=0)[0] for _ in self.targets]

        # Start radar animation
        self.angle = 0  # Current angle of the sweep
        self.anim = FuncAnimation(self.fig, self.update_radar, interval=50)

        # RPM control toggle button
        self.create_rpm_toggle()

    def calculate_sweep_speed(self):
        """Calculate the radar sweep speed in degrees per second based on the RPM."""
        rps = self.rpm / 60.0  # Revolutions per second
        return 360 * rps  # Degrees per second

    def generate_fake_targets(self, num_targets):
        """Generate random fake targets with random angles and distances."""
        targets = []
        for _ in range(num_targets):
            angle = random.uniform(0, 2 * np.pi)  # Random angle (0 to 360 degrees in radians)
            distance = random.uniform(10, 100)  # Random distance from 10 to 100
            alpha = 0  # Initial transparency (completely invisible)
            targets.append([angle, distance, alpha])
        return targets

    def update_radar(self, frame):
        """Update radar sweep and check for targets."""
        # Update the sweep angle
        self.angle = (self.angle + self.sweep_speed * 0.05) % 360  # Increment angle
        angle_rad = np.deg2rad(self.angle)

        # Update the sweep line
        self.sweep_line.set_data([angle_rad, angle_rad], [0, 100])

        # Update target positions and their visibility
        for i, (target_angle, target_distance, alpha) in enumerate(self.targets):
            # Fade the target out gradually if visible
            if alpha > 0:
                alpha -= 0.05  # Reduce alpha each frame
                alpha = max(alpha, 0)  # Ensure alpha doesn't go below 0

            # If radar sweep is within 2 degrees of the target, make it visible again
            if abs(math.degrees(target_angle) - self.angle) < 2:
                alpha = 1.0  # Fully visible when the sweep passes

            # Once the target is completely faded, update its position
            if alpha == 0:
                # Change the target's position (new angle and distance) after it fades out
                new_angle = (target_angle + random.uniform(-TARGET_MOVE_MULTIPLIER, TARGET_MOVE_MULTIPLIER)) % (2 * np.pi)
                new_distance = random.uniform(10, 100)  # New random distance
                self.targets[i][0] = new_angle
                self.targets[i][1] = new_distance

            # Update the target plot
            self.target_plots[i].set_data(target_angle, target_distance)
            self.target_plots[i].set_alpha(alpha)

            # Update the target's alpha value in the list
            self.targets[i][2] = alpha

        # Redraw the canvas
        self.canvas.draw()

    def create_rpm_toggle(self):
        """Create a button to toggle between two RPM values."""
        rpm_frame = tk.Frame(self.root)
        rpm_frame.pack(pady=10)

        # Toggle button to switch RPM
        self.rpm_button = tk.Button(rpm_frame, text=f"Toggle RPM: {self.rpm} RPM", command=self.toggle_rpm)
        self.rpm_button.pack(side=tk.LEFT)

    def toggle_rpm(self):
        """Toggle between RPM_1 and RPM_2."""
        if self.rpm == RPM_1:
            self.rpm = RPM_2
        else:
            self.rpm = RPM_1

        self.sweep_speed = self.calculate_sweep_speed()  # Update sweep speed
        self.rpm_button.config(text=f"Toggle RPM: {self.rpm} RPM")  # Update button label


# Main Tkinter application loop
if __name__ == "__main__":
    root = tk.Tk()
    app = RadarApp(root)
    root.mainloop()
