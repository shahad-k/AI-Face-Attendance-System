import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random

class BirthdayPopup:
    def __init__(self, name, age):
        self.window = tk.Toplevel()
        # Keep window on top and remove borders
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        
        # --- WINDOW POSITIONING ---
        self.w, self.h = 800, 600
        self.screen_w = self.window.winfo_screenwidth()
        self.screen_h = self.window.winfo_screenheight()
        
        # Start the window below the screen for the bounce effect
        self.curr_y = self.screen_h
        self.target_y = (self.screen_h // 2) - (self.h // 2)
        self.target_x = (self.screen_w // 2) - (self.w // 2)
        
        self.window.geometry(f"{self.w}x{self.h}+{self.target_x}+{self.curr_y}")
        
        bg_color = "#FDF0ED" 
        self.window.configure(bg=bg_color)
        
        # --- UI ELEMENTS ---
        self.title_lbl = tk.Label(self.window, text=f"🎉 Happy Birthday, {name}! 🎉", 
                                  font=("Helvetica", 38, "bold"), bg=bg_color, fg="#2C3E50")
        self.title_lbl.pack(pady=(40, 10))
        
        self.subtitle_lbl = tk.Label(self.window, text=f"Wishing you an amazing {age}th year ahead!", 
                                     font=("Helvetica", 20, "italic"), bg=bg_color, fg="#7F8C8D")
        self.subtitle_lbl.pack(pady=(0, 20))
        
        self.gif_label = tk.Label(self.window, bg=bg_color, bd=0)
        self.gif_label.pack(expand=True)
        
        self.timer_lbl = tk.Label(self.window, text="", font=("Helvetica", 22, "bold"), bg=bg_color, fg="#E74C3C")
        self.timer_lbl.pack(pady=20)
        
        # --- LOAD & PROCESS GIF ---
        self.frames = []
        try:
            # Randomly pick one of your 8 green screen cakes
            cake_file = random.choice([f"assets/cake_lit_{i}.gif" for i in range(1, 9)])
            gif = Image.open(cake_file)
            
            temp_frames = []
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert("RGBA")
                
                # 1. CROP THE SIDES
                width, height = frame.size
                crop_pixels = 150  # <-- Tweak this if you still see edges of other cakes
                
                left = crop_pixels
                top = 0
                right = width - crop_pixels
                bottom = height
                
                frame = frame.crop((left, top, right, bottom))
                
                # 2. RESIZE
                frame = frame.resize((350, 350), Image.Resampling.LANCZOS)
                
                # 3. SMART CHROMA KEY
                clean_frame = self.apply_chroma_key(frame)
                temp_frames.append(ImageTk.PhotoImage(clean_frame))
            
            # 4. TIME SKIP (Skip the first 2 seconds of the video so the flame appears immediately)
            frames_to_skip = 40  # <-- Increase this to 50 or 60 if the flame still takes too long to appear
            self.frames = temp_frames[frames_to_skip:]
                
        except Exception as e:
            print(f"Error loading GIF: {e}")
            error_lbl = tk.Label(self.window, text="🎂", font=("Helvetica", 100), bg=bg_color)
            error_lbl.pack(expand=True)
        
        self.frame_index = 0
        
        # Start the sequences
        self.animate()
        self.bounce_in()

    def apply_chroma_key(self, image):
        """Smarter Chroma Key that protects yellow flames and handles shadows."""
        datas = image.getdata()
        new_data = []
        
        for item in datas:
            r, g, b, a = item
            
            # If Green is significantly higher than Red and Blue, it is the background!
            if g > r + 35 and g > b + 35:
                new_data.append((255, 255, 255, 0)) # Make Transparent
            else:
                new_data.append(item)
                
        image.putdata(new_data)
        return image

    def bounce_in(self):
        """Creates the bouncy landing effect."""
        if self.curr_y > self.target_y:
            # Move fast then slow down as it approaches the center
            step = max(5, int((self.curr_y - self.target_y) / 4))
            self.curr_y -= step
            self.window.geometry(f"{self.w}x{self.h}+{self.target_x}+{self.curr_y}")
            self.window.after(20, self.bounce_in)
        else:
            # Once landed, start the 3-second blowing timer
            self.start_countdown(3)

    def start_countdown(self, count):
        """Handles the 3-2-1 timer and the candle blowout."""
        if count > 0:
            self.timer_lbl.config(text=f"Blow out the candle in... {count}")
            self.window.after(1000, lambda: self.start_countdown(count - 1))
        else:
            self.timer_lbl.config(text="Wish Granted! ✨")
            # Freezes animation and closes window gracefully after 2 seconds
            self.window.after(6000, self.window.destroy)

    def animate(self):
        """Loops the GIF frames."""
        if self.frames:
            # Stop animating if the countdown has finished (locks on the last frame)
            if self.timer_lbl.cget("text") != "Wish Granted! ✨":
                self.gif_label.configure(image=self.frames[self.frame_index])
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.window.after(67, self.animate)

# --- TEST FUNCTION (Won't freeze terminal anymore!) ---
if __name__ == "__main__":
    test_root = tk.Tk()
    test_root.withdraw() 
    
    # Spawn the pop-up
    popup = BirthdayPopup("Alex", 16)
    
    # Wait for the pop-up to close, then safely destroy the hidden ghost window
    test_root.wait_window(popup.window)
    test_root.destroy()