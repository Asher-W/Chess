import tkinter as tk
import chessboard as CB

root = tk.Tk()
#edit and save geometry
root.geometry("640x640")
root.resizable(0,0)

CB.ChessBoard(root)

root.mainloop()