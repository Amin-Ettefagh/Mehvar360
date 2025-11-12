
import math, json
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def _fmt(v, nd=3):
    if abs(v) < 1e-9:
        v = 0.0
    return round(float(v), nd)

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sign in")
        self.geometry("460x300")
        self.resizable(True, True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        frame = ctk.CTkFrame(self, corner_radius=14)
        frame.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        title = ctk.CTkLabel(frame, text="Secure Sign In", font=("Inter", 20, "bold"))
        title.grid(row=0, column=0, pady=(16,8))
        self.username = ctk.CTkEntry(frame, placeholder_text="Username")
        self.username.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        self.password = ctk.CTkEntry(frame, placeholder_text="Password", show="•")
        self.password.grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        btn = ctk.CTkButton(frame, text="Enter", command=self.go)
        btn.grid(row=3, column=0, padx=20, pady=(14,18), sticky="ew")
        self.bind("<Return>", lambda e: self.go())

    def go(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            return
        self.withdraw()
        app = MainApp(u, p)
        app.mainloop()
        self.destroy()

class MainApp(ctk.CTk):
    def __init__(self, username, password):
        super().__init__()
        self.title("Vector Path Designer")
        self.geometry("1350x900")
        self.minsize(1100, 700)
        self.username = username
        self.password = password

        self.points = [(0.0, 0.0)]
        self.segments = []
        self.selected_point_index = 0
        self.selected_segment_index = None
        self.tooltip = None

        self.scale = 1.0
        self.offset = (0.0, 0.0)
        self.visual_width = 1
        self.visual_height = 1

        self.grid_columnconfigure(1, weight=1, uniform="x")
        self.grid_rowconfigure(0, weight=1)

        self.left = ctk.CTkFrame(self, corner_radius=12, width=320)
        self.left.grid(row=0, column=0, sticky="nsw", padx=(12,6), pady=12)
        self.left.grid_propagate(False)
        self.left.grid_rowconfigure(12, weight=1)

        self.mid = ctk.CTkFrame(self, corner_radius=12)
        self.mid.grid(row=0, column=1, sticky="nsew", padx=6, pady=12)
        self.mid.grid_rowconfigure(1, weight=1)
        self.mid.grid_columnconfigure(0, weight=1)

        self.right = ctk.CTkFrame(self, corner_radius=12, width=420)
        self.right.grid(row=0, column=2, sticky="nse", padx=(6,12), pady=12)
        self.right.grid_propagate(False)
        self.right.grid_rowconfigure(1, weight=1)

        self.build_left()
        self.build_visual()
        self.build_right()
        self.bind("<Configure>", lambda e: self.redraw())

    def build_left(self):
        title = ctk.CTkLabel(self.left, text="Line Editor", font=("Inter", 18, "bold"))
        title.grid(row=0, column=0, padx=14, pady=(14,6), sticky="w")
        self.start_point_label = ctk.CTkLabel(self.left, text="Start: (0.000, 0.000)")
        self.start_point_label.grid(row=1, column=0, padx=14, pady=6, sticky="w")

        self.base_dir = ctk.CTkOptionMenu(self.left, values=["N","S","E","W"])
        self.base_dir.set("N")
        self.base_dir.grid(row=2, column=0, padx=14, pady=6, sticky="ew")

        self.deg = ctk.CTkEntry(self.left, placeholder_text="Angle (° -360..360)")
        self.deg.grid(row=3, column=0, padx=14, pady=6, sticky="ew")

        self.rot = ctk.CTkOptionMenu(self.left, values=["CW","CCW"])
        self.rot.set("CW")
        self.rot.grid(row=4, column=0, padx=14, pady=6, sticky="ew")

        self.length = ctk.CTkEntry(self.left, placeholder_text="Length (cm)")
        self.length.grid(row=5, column=0, padx=14, pady=6, sticky="ew")

        btn_row = ctk.CTkFrame(self.left)
        btn_row.grid(row=6, column=0, padx=14, pady=10, sticky="ew")
        btn_row.grid_columnconfigure((0,1), weight=1, uniform="b")
        ctk.CTkButton(btn_row, text="Add Line", command=self.add_line).grid(row=0, column=0, padx=(0,6), sticky="ew")
        ctk.CTkButton(btn_row, text="Update Line", command=self.update_line).grid(row=0, column=1, padx=(6,0), sticky="ew")

        ctk.CTkButton(self.left, text="Delete Line", fg_color="#8b1c1c", hover_color="#701515", command=self.delete_line).grid(row=7, column=0, padx=14, pady=(4,10), sticky="ew")

        act_row = ctk.CTkFrame(self.left)
        act_row.grid(row=8, column=0, padx=14, pady=6, sticky="ew")
        act_row.grid_columnconfigure((0,1), weight=1, uniform="a")
        ctk.CTkButton(act_row, text="Auto Complete", command=self.auto_complete).grid(row=0, column=0, padx=(0,6), sticky="ew")
        ctk.CTkButton(act_row, text="Clear All", command=self.clear_all).grid(row=0, column=1, padx=(6,0), sticky="ew")

        io_row = ctk.CTkFrame(self.left)
        io_row.grid(row=10, column=0, padx=14, pady=12, sticky="ew")
        io_row.grid_columnconfigure((0,1), weight=1, uniform="io")
        ctk.CTkButton(io_row, text="Export JSON", command=self.export_json).grid(row=0, column=0, padx=(0,6), sticky="ew")
        ctk.CTkButton(io_row, text="Import JSON", command=self.import_json).grid(row=0, column=1, padx=(6,0), sticky="ew")

    def build_visual(self):
        ctk.CTkLabel(self.mid, text="Visual Preview", font=("Inter", 18, "bold")).grid(row=0, column=0, sticky="nw", padx=12, pady=(12,6))
        self.canvas = tk.Canvas(self.mid, background="#0f1115", highlightthickness=0, cursor="cross")
        self.canvas.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", lambda e: self.hide_tooltip())
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

    def build_right(self):
        ctk.CTkLabel(self.right, text="JSON Preview", font=("Inter", 18, "bold")).grid(row=0, column=0, padx=12, pady=(12,6), sticky="w")
        self.json_box = ctk.CTkTextbox(self.right, height=400, width=420, corner_radius=10)
        self.json_box.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.json_box.configure(state="disabled")
        ctk.CTkLabel(self.right, text="Click a line to edit. Click a point to set the next start.", text_color="#a0a4ad", wraplength=380, justify="left").grid(row=2, column=0, padx=12, pady=(0,12), sticky="ew")
        self.update_panels()

    def base_heading(self, d):
        return {"E":0.0,"N":90.0,"W":180.0,"S":270.0}[d]

    def add_line(self):
        try:
            d = self.base_dir.get().strip()
            a = float(self.deg.get().strip() or "0")
            r = self.rot.get().strip()
            l = float(self.length.get().strip())
        except:
            return
        a = max(-360.0, min(360.0, a))
        start = self.points[self.selected_point_index]
        base = self.base_heading(d)
        heading = base - a if r == "CW" else base + a
        rad = math.radians(heading)
        dx = l * math.cos(rad)
        dy = l * math.sin(rad)
        end = (start[0] + dx, start[1] + dy)
        self.segments.append({"start_index": self.selected_point_index, "end_index": len(self.points), "base": d, "angle": a, "rotation": r, "length_cm": l})
        self.points.append(end)
        self.selected_point_index = len(self.points) - 1
        self.selected_segment_index = len(self.segments) - 1
        self.update_panels()

    def update_line(self):
        if self.selected_segment_index is None:
            return
        i = self.selected_segment_index
        si = self.segments[i]["start_index"]
        try:
            d = self.base_dir.get().strip()
            a = float(self.deg.get().strip() or "0")
            r = self.rot.get().strip()
            l = float(self.length.get().strip())
        except:
            return
        a = max(-360.0, min(360.0, a))
        base = self.base_heading(d)
        heading = base - a if r == "CW" else base + a
        rad = math.radians(heading)
        dx = l * math.cos(rad)
        dy = l * math.sin(rad)
        start = self.points[si]
        end = (start[0] + dx, start[1] + dy)
        self.points[self.segments[i]["end_index"]] = end
        self.segments[i] = {"start_index": si, "end_index": self.segments[i]["end_index"], "base": d, "angle": a, "rotation": r, "length_cm": l}
        self.rebuild_from(si)
        self.update_panels()

    def delete_line(self):
        if self.selected_segment_index is None:
            return
        idx = self.selected_segment_index
        end_index = self.segments[idx]["end_index"]
        del self.segments[idx]
        used = set()
        for s in self.segments:
            used.add(s["start_index"])
            used.add(s["end_index"])
        if end_index not in used and end_index < len(self.points):
            self.points.pop(end_index)
            for s in self.segments:
                if s["start_index"] > end_index:
                    s["start_index"] -= 1
                if s["end_index"] > end_index:
                    s["end_index"] -= 1
        self.selected_segment_index = None
        if self.segments:
            self.selected_point_index = self.segments[-1]["end_index"]
        else:
            self.points = [(0.0,0.0)]
            self.selected_point_index = 0
        self.update_panels()

    def auto_complete(self):
        if len(self.points) < 2:
            return
        start = self.points[self.selected_point_index]
        target = self.points[0]
        if start == target:
            return
        vx = target[0] - start[0]
        vy = target[1] - start[1]
        heading = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0
        bases = {"E":0.0,"N":90.0,"W":180.0,"S":270.0}
        best = None
        for k, b in bases.items():
            diff = (heading - b + 360.0) % 360.0
            cw_angle = (b - heading + 360.0) % 360.0
            ccw_angle = diff
            if cw_angle <= ccw_angle:
                angle = cw_angle
                rot = "CW"
            else:
                angle = ccw_angle
                rot = "CCW"
            if best is None or angle < best[0]:
                best = (angle, k, rot)
        angle, base_dir, rot = best
        length = math.hypot(vx, vy)
        self.base_dir.set(base_dir)
        self.deg.delete(0, tk.END); self.deg.insert(0, f"{angle:.3f}")
        self.rot.set(rot)
        self.length.delete(0, tk.END); self.length.insert(0, f"{length:.3f}")
        self.add_line()

    def clear_all(self):
        self.points = [(0.0,0.0)]
        self.segments = []
        self.selected_point_index = 0
        self.selected_segment_index = None
        self.update_panels()

    def export_json(self):
        data = self.build_json_data()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")], title="Save JSON As")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")], title="Open JSON")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            return
        up = data.get("auth", {})
        self.username = up.get("username", self.username)
        self.password = up.get("password", self.password)
        pts = data.get("points")
        segs = data.get("segments")
        if isinstance(pts, list) and isinstance(segs, list) and len(pts) >= 1:
            self.points = [(float(p[0]), float(p[1])) for p in pts]
            self.segments = []
            for s in segs:
                self.segments.append({
                    "start_index": int(s["start_index"]),
                    "end_index": int(s["end_index"]),
                    "base": s["base"],
                    "angle": float(s["angle"]),
                    "rotation": s["rotation"],
                    "length_cm": float(s["length_cm"]),
                })
            self.selected_point_index = self.segments[-1]["end_index"] if self.segments else 0
            self.selected_segment_index = None
            self.update_panels()

    def build_json_data(self):
        cleaned_points = [[_fmt(p[0]), _fmt(p[1])] for p in self.points]
        lines = []
        for i, s in enumerate(self.segments):
            sp = self.points[s["start_index"]]
            ep = self.points[s["end_index"]]
            a = {
                "index": i,
                "start_index": s["start_index"],
                "end_index": s["end_index"],
                "start_point": {"x": _fmt(sp[0]), "y": _fmt(sp[1])},
                "end_point": {"x": _fmt(ep[0]), "y": _fmt(ep[1])},
                "base": s["base"],
                "angle": _fmt(s["angle"]),
                "rotation": s["rotation"],
                "length_cm": _fmt(s["length_cm"]),
            }
            lines.append(a)
        data = {
            "auth": {"username": self.username, "password": self.password},
            "points": cleaned_points,
            "segments": lines
        }
        return data

    def update_panels(self):
        self.start_point_label.configure(text=f"Start: ({_fmt(self.points[self.selected_point_index][0]):.3f}, {_fmt(self.points[self.selected_point_index][1]):.3f})")
        self.json_box.configure(state="normal")
        self.json_box.delete("1.0", "end")
        self.json_box.insert("1.0", json.dumps(self.build_json_data(), indent=2))
        self.json_box.configure(state="disabled")
        self.redraw()

    def rebuild_from(self, start_index):
        order = sorted([(i, s) for i, s in enumerate(self.segments)], key=lambda x: x[0])
        for i, s in order:
            if s["start_index"] >= start_index:
                base = self.base_heading(s["base"])
                heading = base - s["angle"] if s["rotation"] == "CW" else base + s["angle"]
                rad = math.radians(heading)
                dx = s["length_cm"] * math.cos(rad)
                dy = s["length_cm"] * math.sin(rad)
                sp = self.points[s["start_index"]]
                ep = (sp[0] + dx, sp[1] + dy)
                self.points[s["end_index"]] = ep

    def get_bounds(self):
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        if not xs or not ys:
            return (-1, -1, 1, 1)
        return (min(xs), min(ys), max(xs), max(ys))

    def world_to_screen(self, x, y):
        sx = (x * self.scale) + self.offset[0]
        sy = self.visual_height - ((y * self.scale) + self.offset[1])
        return sx, sy

    def compute_view(self):
        w = max(self.canvas.winfo_width(), 10)
        h = max(self.canvas.winfo_height(), 10)
        self.visual_width = w
        self.visual_height = h
        xmin, ymin, xmax, ymax = self.get_bounds()
        wspan = max(1.0, xmax - xmin)
        hspan = max(1.0, ymax - ymin)
        margin = 60.0
        sx = (w - 2*margin) / wspan
        sy = (h - 2*margin) / hspan
        self.scale = max(0.1, min(sx, sy))
        if len(self.segments) <= 1:
            sp = self.points[0]
            self.offset = (w/2 - sp[0]*self.scale, (h - h/2) - sp[1]*self.scale)
        else:
            cxw = (xmin + xmax) / 2.0
            cyw = (ymin + ymax) / 2.0
            cxs = w / 2.0
            cys = h / 2.0
            self.offset = (cxs - cxw * self.scale, (h - cys) - cyw * self.scale)

    def redraw(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        self.compute_view()
        for i, s in enumerate(self.segments):
            sp = self.points[s["start_index"]]
            ep = self.points[s["end_index"]]
            x1,y1 = self.world_to_screen(sp[0], sp[1])
            x2,y2 = self.world_to_screen(ep[0], ep[1])
            w = 3 if i == self.selected_segment_index else 2
            cid = self.canvas.create_line(x1,y1,x2,y2, fill="#60a5fa", width=w, tags=("seg", f"seg_{i}"))
            self.canvas.tag_bind(cid, "<Enter>", lambda e, idx=i: self.on_hover_line(idx, e))
            self.canvas.tag_bind(cid, "<Leave>", lambda e: self.hide_tooltip())
            self.canvas.tag_bind(cid, "<Button-1>", lambda e, idx=i: self.select_segment(idx))
        for idx, p in enumerate(self.points):
            x,y = self.world_to_screen(p[0], p[1])
            r = 6 if idx == self.selected_point_index else 4
            fill = "#22c55e" if idx == self.selected_point_index else "#94a3b8"
            pid = self.canvas.create_oval(x-r,y-r,x+r,y+r, fill=fill, outline="", tags=("pt", f"pt_{idx}"))
            self.canvas.tag_bind(pid, "<Enter>", lambda e, i=idx: self.on_hover_point(i, e))
            self.canvas.tag_bind(pid, "<Leave>", lambda e: self.hide_tooltip())
            self.canvas.tag_bind(pid, "<Button-1>", lambda e, i=idx: self.select_point(i))

    def on_hover_point(self, idx, event):
        p = self.points[idx]
        text = f"Point #{idx}\\nX: {_fmt(p[0]):.3f}\\nY: {_fmt(p[1]):.3f}"
        self.show_tooltip(event.x_root, event.y_root, text)

    def on_hover_line(self, idx, event):
        s = self.segments[idx]
        sp = self.points[s["start_index"]]
        ep = self.points[s["end_index"]]
        text = f"Line #{idx}\\nStart: ({_fmt(sp[0]):.3f}, {_fmt(sp[1]):.3f})\\nEnd: ({_fmt(ep[0]):.3f}, {_fmt(ep[1]):.3f})\\nBase: {s['base']}  Angle: {_fmt(s['angle']):.3f}°  {s['rotation']}\\nLength: {_fmt(s['length_cm']):.3f} cm"
        self.show_tooltip(event.x_root, event.y_root, text)

    def on_motion(self, event):
        pass

    def on_click(self, event):
        pass

    def select_point(self, idx):
        self.selected_point_index = idx
        self.selected_segment_index = None
        self.update_panels()

    def select_segment(self, idx):
        self.selected_segment_index = idx
        s = self.segments[idx]
        self.base_dir.set(s["base"])
        self.deg.delete(0, tk.END); self.deg.insert(0, str(s["angle"]))
        self.rot.set(s["rotation"])
        self.length.delete(0, tk.END); self.length.insert(0, str(s["length_cm"]))
        self.selected_point_index = s["start_index"]
        self.update_panels()

    def show_tooltip(self, rx, ry, text):
        self.hide_tooltip()
        self.tooltip = ctk.CTkToplevel(self)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        lbl = ctk.CTkLabel(self.tooltip, text=text, fg_color="#111827", corner_radius=10, padx=10, pady=8)
        lbl.pack()
        self.tooltip.update_idletasks()
        w = self.tooltip.winfo_width()
        h = self.tooltip.winfo_height()
        self.tooltip.geometry(f"{w}x{h}+{int(rx)+12}+{int(ry)+12}")

    def hide_tooltip(self):
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except:
                pass
            self.tooltip = None

if __name__ == "__main__":
    Login().mainloop()
