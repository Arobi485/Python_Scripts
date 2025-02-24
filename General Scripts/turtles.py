import turtle

def draw_tree(branch_length, t):
    if branch_length > 5:
        # Draw the branch
        t.forward(branch_length)
        # Turn right
        t.right(20)
        # Draw the right subtree
        draw_tree(branch_length - 15, t)
        # Turn left
        t.left(40)
        # Draw the left subtree
        draw_tree(branch_length - 15, t)
        # Turn right
        t.right(20)
        # Go back to the previous position
        t.backward(branch_length)

def main():
    t = turtle.Turtle()
    my_win = turtle.Screen()
    t.left(90)          # Point the turtle upwards
    t.up()
    t.backward(100)     # Move the turtle to a better starting position
    t.down()
    t.color("green")
    draw_tree(200, t)
    my_win.exitonclick()

if __name__ == "__main__":
    main()