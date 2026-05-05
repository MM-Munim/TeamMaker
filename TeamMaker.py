import tkinter as tk
from tkinter import ttk, messagebox
import random

# ── Palette ────────────────────────────────────────────────────────────────────
BG        = "#F7F6F3"
SURFACE   = "#FFFFFF"
BORDER    = "#E0DDD6"
TEXT      = "#1A1A18"
MUTED     = "#777770"
PRIMARY   = "#1A1A18"
PRIMARY_T = "#FFFFFF"
BTN_HOV   = "#F0EDE8"
ERR_BG    = "#FEF0EF"
ERR_FG    = "#C0392B"
HDR_BG    = "#F0EDE8"
POT_COLORS = ["#378ADD", "#1D9E75", "#D85A30", "#D4537E", "#BA7517",
              "#7F77DD", "#639922", "#E24B4A", "#0F6E56", "#993556"]


# ── Helpers ────────────────────────────────────────────────────────────────────
def distribute(players: list, n_teams: int) -> list[list]:
    """
    Distributes players by floor then remainder randomly.
    Ensures even distribution as requested.
    """
    shuffled = players[:]
    random.shuffle(shuffled)
    
    num_players = len(shuffled)
    base_count = num_players // n_teams
    remainder = num_players % n_teams
    
    buckets = []
    current_idx = 0
    
    # Randomize which teams get the extra players
    extra_player_indices = random.sample(range(n_teams), remainder)
    
    for i in range(n_teams):
        count = base_count + (1 if i in extra_player_indices else 0)
        buckets.append(shuffled[current_idx : current_idx + count])
        current_idx += count
        
    return buckets


# ── StyledButton ───────────────────────────────────────────────────────────────
class StyledButton(tk.Frame):
    def __init__(self, parent, text, command=None, style="default", **kwargs):
        bg     = SURFACE if style == "default" else PRIMARY
        border = BORDER  if style == "default" else PRIMARY
        super().__init__(parent, bg=bg, highlightthickness=1,
                         highlightbackground=border, cursor="hand2")
        self._style = style
        self._cmd   = command
        self._bg    = bg
        fg = TEXT if style == "default" else PRIMARY_T
        self._lbl = tk.Label(self, text=text, bg=bg, fg=fg,
                             font=("Helvetica", 12), padx=18, pady=9,
                             cursor="hand2")
        self._lbl.pack()
        for w in (self, self._lbl):
            w.bind("<Button-1>", self._click)
            w.bind("<Enter>",    self._enter)
            w.bind("<Leave>",    self._leave)

    def _click(self, _=None):
        if self._cmd:
            self._cmd()

    def _enter(self, _=None):
        hov = BTN_HOV if self._style == "default" else "#333330"
        self._lbl.config(bg=hov)
        self.config(bg=hov)

    def _leave(self, _=None):
        self._lbl.config(bg=self._bg)
        self.config(bg=self._bg)

    def set_text(self, t):
        self._lbl.config(text=t)


# ── PlayerRow ──────────────────────────────────────────────────────────────────
class PlayerRow(tk.Frame):
    def __init__(self, parent, on_remove, **kwargs):
        super().__init__(parent, bg=SURFACE)
        self._entry = tk.Entry(self, bg=BG, fg=TEXT, relief="flat",
                               font=("Helvetica", 12), insertbackground=TEXT)
        self._entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 4))
        self._rm = tk.Label(self, text="×", bg=SURFACE, fg=MUTED,
                            font=("Helvetica", 14), cursor="hand2", padx=4)
        self._rm.pack(side="right")
        self._rm.bind("<Button-1>", lambda _: on_remove(self))
        self._rm.bind("<Enter>",    lambda _: self._rm.config(fg=ERR_FG))
        self._rm.bind("<Leave>",    lambda _: self._rm.config(fg=MUTED))

    @property
    def name(self):
        return self._entry.get().strip()

    def focus(self):
        self._entry.focus_set()


# ── PotFrame ───────────────────────────────────────────────────────────────────
class PotFrame(tk.Frame):
    def __init__(self, parent, index: int, on_remove, **kwargs):
        super().__init__(parent, bg=SURFACE, highlightthickness=1,
                         highlightbackground=BORDER)
        self.index = index
        self._on_remove = on_remove
        self._player_rows: list[PlayerRow] = []
        self._collapsed = False
        self._build()

    def _build(self):
        # Header
        self.hdr = tk.Frame(self, bg=SURFACE)
        self.hdr.pack(fill="x", padx=12, pady=(10, 6))

        # Collapse/Expand Toggle
        self._toggle_lbl = tk.Label(self.hdr, text="▼", bg=SURFACE, fg=MUTED, 
                                    font=("Helvetica", 10), cursor="hand2", width=2)
        self._toggle_lbl.pack(side="left", padx=(0, 4))
        self._toggle_lbl.bind("<Button-1>", lambda _: self.toggle_collapse())

        color = POT_COLORS[self.index % len(POT_COLORS)]
        dot = tk.Canvas(self.hdr, width=10, height=10, bg=SURFACE, highlightthickness=0)
        dot.create_oval(1, 1, 9, 9, fill=color, outline="")
        dot.pack(side="left", padx=(0, 8))

        self._name_var = tk.StringVar(value=f"Pot {self.index + 1}")
        tk.Entry(self.hdr, textvariable=self._name_var, bg=SURFACE, fg=TEXT,
                 relief="flat", font=("Helvetica", 13, "bold"),
                 insertbackground=TEXT, width=14).pack(side="left")

        self._count_lbl = tk.Label(self.hdr, text="0 players", bg=SURFACE, fg=MUTED,
                                   font=("Helvetica", 11))
        self._count_lbl.pack(side="left", padx=(8, 0))

        rm = tk.Label(self.hdr, text="×", bg=SURFACE, fg=MUTED,
                      font=("Helvetica", 14), cursor="hand2")
        rm.pack(side="right")
        rm.bind("<Button-1>", lambda _: self._on_remove(self))
        rm.bind("<Enter>",    lambda _: rm.config(fg=ERR_FG))
        rm.bind("<Leave>",    lambda _: rm.config(fg=MUTED))

        self.sep = tk.Frame(self, bg=BORDER, height=1)
        self.sep.pack(fill="x")

        # Players Container
        self._body = tk.Frame(self, bg=SURFACE)
        self._body.pack(fill="x")

        # Players list
        self._players_frame = tk.Frame(self._body, bg=SURFACE)
        self._players_frame.pack(fill="x", padx=12, pady=6)

        # Add player link
        self._add_btn = tk.Label(self._body, text="+ add player", bg=SURFACE, fg=MUTED,
                       font=("Helvetica", 11), cursor="hand2", pady=7)
        self._add_btn.pack(fill="x", padx=12)
        self._add_btn.bind("<Button-1>", lambda _: self.add_player())
        self._add_btn.bind("<Enter>",    lambda _: self._add_btn.config(fg=TEXT))
        self._add_btn.bind("<Leave>",    lambda _: self._add_btn.config(fg=MUTED))

        tk.Frame(self._body, bg=BORDER, height=1).pack(fill="x")

        self.add_player()

    def toggle_collapse(self):
        if self._collapsed:
            self._body.pack(fill="x", after=self.sep)
            self._toggle_lbl.config(text="▼")
        else:
            self._body.pack_forget()
            self._toggle_lbl.config(text="▶")
        self._collapsed = not self._collapsed

    @property
    def pot_name(self):
        return self._name_var.get().strip() or f"Pot {self.index + 1}"

    @property
    def color(self):
        return POT_COLORS[self.index % len(POT_COLORS)]

    def add_player(self, name=""):
        row = PlayerRow(self._players_frame, on_remove=self._remove_player)
        row.pack(fill="x", pady=2)
        if name:
            row._entry.insert(0, name)
        self._player_rows.append(row)
        self._refresh_count()
        row.focus()

    def valid_players(self):
        self._refresh_count()
        return [r.name for r in self._player_rows if r.name]

    def _remove_player(self, row: PlayerRow):
        if len(self._player_rows) <= 1:
            return
        row.destroy()
        self._player_rows.remove(row)
        self._refresh_count()

    def _refresh_count(self):
        n = len([r for r in self._player_rows if r.name])
        self._count_lbl.config(text=f"{n} player{'s' if n != 1 else ''}")


# ── Scrollable canvas factory ──────────────────────────────────────────────────
def make_scroll_area(parent, bg=BG):
    outer   = tk.Frame(parent, bg=bg)
    canvas  = tk.Canvas(outer, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner   = tk.Frame(canvas, bg=bg)

    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.bind("<Configure>",
                lambda e, wid=win_id: canvas.itemconfig(wid, width=e.width))

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    return outer, inner, canvas


# ── Main App ───────────────────────────────────────────────────────────────────
class TeamMakerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Team Maker")
        self.geometry("760x680")
        self.minsize(640, 480)
        self.config(bg=BG)
        self._pot_frames: list[PotFrame] = []
        self._scroll_target = None
        self._build_ui()

    def _build_ui(self):
        # ══════════════ LEFT PANEL ════════════════════════════════════════════
        left_outer = tk.Frame(self, bg=BG, width=340)
        left_outer.pack(side="left", fill="both", expand=False, padx=(20, 10), pady=20)
        left_outer.pack_propagate(False)

        top = tk.Frame(left_outer, bg=BG)
        top.pack(side="top", fill="x")

        tk.Label(top, text="Team Maker", bg=BG, fg=TEXT,
                 font=("Helvetica", 18, "bold")).pack(anchor="w")
        tk.Label(top, text="Set up pots, add players, run the draw.",
                 bg=BG, fg=MUTED, font=("Helvetica", 11)).pack(anchor="w", pady=(2, 14))
        
        tk.Label(top, text="NUMBER OF TEAMS", bg=BG, fg=MUTED,
                 font=("Helvetica", 10)).pack(anchor="w", pady=(0, 6))

        ctrl = tk.Frame(top, bg=BG)
        ctrl.pack(anchor="w", pady=(0, 14))
        self._n_teams = tk.IntVar(value=4)
        tk.Button(ctrl, text="−", bg=SURFACE, fg=TEXT, relief="flat",
                  font=("Helvetica", 14), width=2, cursor="hand2",
                  command=lambda: self._change_teams(-1)).pack(side="left")
        tk.Label(ctrl, textvariable=self._n_teams, bg=BG, fg=TEXT,
                 font=("Helvetica", 22, "bold"), width=3,
                 anchor="center").pack(side="left")
        tk.Button(ctrl, text="+", bg=SURFACE, fg=TEXT, relief="flat",
                  font=("Helvetica", 14), width=2, cursor="hand2",
                  command=lambda: self._change_teams(1)).pack(side="left")

        tk.Frame(top, bg=BORDER, height=1).pack(fill="x", pady=(0, 10))
        tk.Label(top, text="POTS & PLAYERS", bg=BG, fg=MUTED,
                 font=("Helvetica", 10)).pack(anchor="w", pady=(0, 8))

        bottom = tk.Frame(left_outer, bg=BG)
        bottom.pack(side="bottom", fill="x")

        add_pot = tk.Label(bottom, text="+ add pot", bg=BG, fg=MUTED,
                           font=("Helvetica", 12), cursor="hand2", pady=8)
        add_pot.pack(fill="x")
        add_pot.bind("<Button-1>", lambda _: self._add_pot())

        self._err_lbl = tk.Label(bottom, text="", bg=ERR_BG, fg=ERR_FG,
                                 font=("Helvetica", 11), wraplength=300,
                                 justify="left", padx=10, pady=6)

        self._draw_btn = StyledButton(bottom, text="Generate Teams →",
                                      command=self._run_draw, style="primary")
        self._draw_btn.pack(fill="x", pady=(4, 0))

        scroll_outer, self._pots_inner, left_canvas = make_scroll_area(left_outer)
        scroll_outer.pack(side="top", fill="both", expand=True)
        self._left_canvas = left_canvas
        left_canvas.bind("<Enter>", lambda _: self._set_scroll(left_canvas))

        self._add_pot()
        self._add_pot()

        # ══════════════ DIVIDER ═══════════════════════════════════════════════
        tk.Frame(self, bg=BORDER, width=1).pack(side="left", fill="y", pady=20)

        # ══════════════ RIGHT PANEL ═══════════════════════════════════════════
        right_outer = tk.Frame(self, bg=BG)
        right_outer.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=20)

        tk.Label(right_outer, text="Results", bg=BG, fg=TEXT,
                 font=("Helvetica", 14, "bold")).pack(anchor="w")
        self._results_sub = tk.Label(right_outer, text="Final teams will appear here.",
                                     bg=BG, fg=MUTED, font=("Helvetica", 11))
        self._results_sub.pack(anchor="w", pady=(2, 12))

        res_outer, self._results_frame, right_canvas = make_scroll_area(right_outer)
        res_outer.pack(fill="both", expand=True)
        self._right_canvas = right_canvas
        right_canvas.bind("<Enter>", lambda _: self._set_scroll(right_canvas))

        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _set_scroll(self, canvas):
        self._scroll_target = canvas

    def _on_mousewheel(self, event):
        if self._scroll_target:
            self._scroll_target.yview_scroll(-1 * (event.delta // 120), "units")

    def _change_teams(self, delta):
        self._n_teams.set(max(2, min(16, self._n_teams.get() + delta)))

    def _add_pot(self):
        idx = len(self._pot_frames)
        pf = PotFrame(self._pots_inner, index=idx, on_remove=self._remove_pot)
        pf.pack(fill="x", pady=(0, 8), padx=2)
        self._pot_frames.append(pf)

    def _remove_pot(self, pf: PotFrame):
        if len(self._pot_frames) <= 1: return
        pf.destroy()
        self._pot_frames.remove(pf)

    def _run_draw(self):
        n = self._n_teams.get()
        # Initialize teams with editable names
        teams = [{"name": f"Team {i + 1}", "slots": []} for i in range(n)]
        
        for pf in self._pot_frames:
            players = pf.valid_players()
            if not players: continue
            
            buckets = distribute(players, n)
            for i, bucket in enumerate(buckets):
                for player in bucket:
                    teams[i]["slots"].append((pf.pot_name, pf.color, player))

        self._render_results(teams)

    def _render_results(self, teams):
        for w in self._results_frame.winfo_children(): w.destroy()
        self._results_sub.config(text="Edit team names below if needed.")

        for team in teams:
            card = tk.Frame(self._results_frame, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
            card.pack(fill="x", pady=(0, 10))

            hdr = tk.Frame(card, bg=HDR_BG)
            hdr.pack(fill="x")
            
            # Editable Team Name
            t_name_var = tk.StringVar(value=team["name"])
            tk.Entry(hdr, textvariable=t_name_var, bg=HDR_BG, fg=TEXT, relief="flat",
                     font=("Helvetica", 12, "bold"), width=20).pack(side="left", padx=12, pady=7)
            
            count = len(team["slots"])
            tk.Label(hdr, text=f"{count} players", bg=HDR_BG, fg=MUTED, font=("Helvetica", 10)).pack(side="right", padx=12)

            for (pot_name, color, player) in team["slots"]:
                row = tk.Frame(card, bg=SURFACE)
                row.pack(fill="x", padx=12, pady=3)
                tk.Label(row, text=pot_name, bg=SURFACE, fg=color, font=("Helvetica", 10), width=10, anchor="w").pack(side="left")
                tk.Label(row, text=player, bg=SURFACE, fg=TEXT, font=("Helvetica", 12)).pack(side="left")

        self._right_canvas.yview_moveto(0.0)

if __name__ == "__main__":
    app = TeamMakerApp()
    app.mainloop()