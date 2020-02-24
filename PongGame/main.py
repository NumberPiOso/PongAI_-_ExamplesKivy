from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
import numpy as np
from sklearn.linear_model import LinearRegression

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    # Modification to train AI.
    # Player 2
    max_velocity_paddle = 1
    # Player 1
    take_input = False
    take_output = True
    X_i = None
    y_i = None
    # Game in general
    training_data = []
    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)
        

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # Ready for getting input data
        if self.ball.x > self.width/2:
            self.take_input = True
        # Define self.X_i (input)
        if self.take_input:
            if self.ball.x < self.width/2:
                ball = self.ball
                self.X_i = ball.x, ball.y, ball.velocity_x, ball.velocity_y
                self.take_input = False
                self.take_output = True
                # Move player 1!
                self.player1.center_y = float(model.predict([self.X_i])[0])
        # Move player 1 and define self.y_i (output)
        if self.take_output: 
            if self.ball.x < self.width/9:
                self.y_i = self.ball.y
                self.training_data.append([*self.X_i, self.y_i])
                self.take_output = False
                print(f'Input is {self.X_i}')
                print(f'Output should be: {self.y_i}')
                print(f'Prediction was: {float(model.predict([self.X_i])[0])}')
        
        
        # player 2 follows the ball with max velocity predefined
        self.player2.center_y += float(np.clip(self.ball.y-self.player2.center_y, 
            -self.max_velocity_paddle, self.max_velocity_paddle))

        # went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    def player_2_follows_ball(self):
        """This is the first step to do a ML player, is simply
            instructions for player two to follow the ball."""
        self.player2.center_y = self.ball.y

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game



if __name__ == '__main__':
    # Get data
    data = np.loadtxt('training_data.txt', max_rows=15000)
    X, y = data[:, :-1], data[:, -1]
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    PongApp().run()
    
    # Save data to keep training
    training_data = np.array(PongGame.training_data)
    np.savetxt('batch_training.txt', training_data)
    with open("training_data.txt","a") as file_out, \
            open("batch_training.txt") as file_in:
        for line in file_in:
            file_out.write(line)