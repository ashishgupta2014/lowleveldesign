from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


# --- Strategy Pattern for Moves ---
class MoveStrategy(ABC):
    @abstractmethod
    def get_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        pass


class KingStrategy(MoveStrategy):
    def get_moves(self, pos, board):
        r, c = pos
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if board.is_inside(nr, nc):
                    moves.append((nr, nc))
        return moves


class RookStrategy(MoveStrategy):
    def get_moves(self, pos, board):
        r, c = pos
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while board.is_inside(nr, nc) and board.grid[nr][nc] is None:
                moves.append((nr, nc))
                nr += dr
                nc += dc
            if board.is_inside(nr, nc) and board.grid[nr][nc] is not None:
                moves.append((nr, nc))
        return moves


class BishopStrategy(MoveStrategy):
    def get_moves(self, pos, board):
        r, c = pos
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while board.is_inside(nr, nc) and board.grid[nr][nc] is None:
                moves.append((nr, nc))
                nr += dr
                nc += dc
            if board.is_inside(nr, nc) and board.grid[nr][nc] is not None:
                moves.append((nr, nc))
        return moves


class QueenStrategy(MoveStrategy):
    def get_moves(self, pos, board):
        # Queen = Rook + Bishop moves
        return RookStrategy().get_moves(pos, board) + BishopStrategy().get_moves(pos, board)


class KnightStrategy(MoveStrategy):
    def get_moves(self, pos, board):
        r, c = pos
        moves = []
        jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in jumps:
            nr, nc = r + dr, c + dc
            if board.is_inside(nr, nc):
                moves.append((nr, nc))
        return moves


class PawnStrategy(MoveStrategy):
    def __init__(self, color: str):
        self.color = color

    def get_moves(self, pos, board):
        r, c = pos
        moves = []
        direction = -1 if self.color == "White" else 1
        # Forward move
        nr, nc = r + direction, c
        if board.is_inside(nr, nc) and board.grid[nr][nc] is None:
            moves.append((nr, nc))
        # Captures
        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if board.is_inside(nr, nc) and board.grid[nr][nc] is not None:
                moves.append((nr, nc))
        return moves


# --- Piece Class ---
class Piece:
    def __init__(self, name: str, color: str, strategy: MoveStrategy):
        self.name = name
        self.color = color
        self.strategy = strategy

    def possible_moves(self, pos, board):
        return self.strategy.get_moves(pos, board)


# --- Board Class ---
class Board:
    def __init__(self):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]

    def is_inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def place_piece(self, piece: Piece, pos: Tuple[int, int]):
        r, c = pos
        self.grid[r][c] = piece

    def move_piece(self, src: Tuple[int, int], dst: Tuple[int, int]):
        r1, c1 = src
        r2, c2 = dst
        piece = self.grid[r1][c1]
        if piece is None:
            raise ValueError("No piece at source")
        self.grid[r1][c1] = None
        self.grid[r2][c2] = piece

    def show(self):
        for r in range(8):
            row = []
            for c in range(8):
                p = self.grid[r][c]
                row.append(p.name[0] if p else ".")
            print(" ".join(row))
        print()


# --- Example Driver ---
if __name__ == "__main__":
    board = Board()

    # Place pieces
    king = Piece("King", "White", KingStrategy())
    rook = Piece("Rook", "Black", RookStrategy())
    queen = Piece("Queen", "White", QueenStrategy())
    knight = Piece("Knight", "Black", KnightStrategy())
    pawn = Piece("Pawn", "White", PawnStrategy("White"))

    board.place_piece(king, (4, 4))
    board.place_piece(rook, (0, 0))
    board.place_piece(queen, (7, 7))
    board.place_piece(knight, (2, 5))
    board.place_piece(pawn, (6, 3))

    board.show()

    print("King moves:", king.possible_moves((4, 4), board))
    print("Rook moves:", rook.possible_moves((0, 0), board))
    print("Queen moves:", queen.possible_moves((7, 7), board))
    print("Knight moves:", knight.possible_moves((2, 5), board))
    print("Pawn moves:", pawn.possible_moves((6, 3), board))
