from tkinter import Tk, Frame, BOTH, Button, RIGHT
from tkinter import NW, Canvas
from PIL import Image, ImageTk
import math
import random



FIRE_RGBS = (
    (0x07, 0x07, 0x07),
    (0x1F, 0x07, 0x07),
    (0x2F, 0x0F, 0x07),
    (0x47, 0x0F, 0x07),
    (0x57, 0x17, 0x07),
    (0x67, 0x1F, 0x07),
    (0x77, 0x1F, 0x07),
    (0x8F, 0x27, 0x07),
    (0x9F, 0x2F, 0x07),
    (0xAF, 0x3F, 0x07),
    (0xBF, 0x47, 0x07),
    (0xC7, 0x47, 0x07),
    (0xDF, 0x4F, 0x07),
    (0xDF, 0x57, 0x07),
    (0xDF, 0x57, 0x07),
    (0xD7, 0x5F, 0x07),
    (0xD7, 0x5F, 0x07),
    (0xD7, 0x67, 0x0F),
    (0xCF, 0x6F, 0x0F),
    (0xCF, 0x77, 0x0F),
    (0xCF, 0x7F, 0x0F),
    (0xCF, 0x87, 0x17),
    (0xC7, 0x87, 0x17),
    (0xC7, 0x8F, 0x17),
    (0xC7, 0x97, 0x1F),
    (0xBF, 0x9F, 0x1F),
    (0xBF, 0x9F, 0x1F),
    (0xBF, 0xA7, 0x27),
    (0xBF, 0xA7, 0x27),
    (0xBF, 0xAF, 0x2F),
    (0xB7, 0xAF, 0x2F),
    (0xB7, 0xB7, 0x2F),
    (0xB7, 0xB7, 0x37),
    (0xCF, 0xCF, 0x6F),
    (0xDF, 0xDF, 0x9F),
    (0xEF, 0xEF, 0xC7),
    (0xFF, 0xFF, 0xFF),
)


def draw_line(px_handle, x1: int, y1: int, x2: int, y2: int, color = (0, 0, 0)):
    """Brezenhem - algorithm drawing line"""
    lx = abs(x1 - x2)            # define lengths
    ly = abs(y1 - y2)

    swap = ly >= lx
    if swap:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        lx, ly = ly, lx

    dy = 1 if y1 < y2 else -1    # define direct line
    dx = 1 if x1 < x2 else -1

    err = 0
    derr = ly + 1
    while x1 != x2:
        px_handle[(y1, x1) if swap else (x1, y1)] = color
        x1 += dx
        err += derr
        if err >= lx + 1:
            err -= lx + 1
            y1 += dy


class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if type(other) == Vector2D:
            return self.x * other.x + self.y * other.y
        else:
            return Vector2D(self.x * other, self.y * other)

    def copy(self):
        return Vector2D(self.x, self.y)

    def __rmull__(self, other):
        return self * other

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def angle(self):
        return math.atan2(self.y, self.x)

    @classmethod
    def new_vector(cls, **kwargs):
        xy = kwargs.get("xy")
        if xy is not None:
            return cls(xy[0], xy[1])
        angle = kwargs.get("angle", 0)
        length = kwargs.get("length", 1)
        if length < 0:
            raise ValueError("ParameterError: Uncorrect length value!!!")
        return cls(length * math.cos(angle), length * math.sin(angle))

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def int_xy(self):
        self.x = int(self.x)
        self.y = int(self.y)

    def round_xy(self, count = 0):
        self.x = round(self.x, count)
        self.y = round(self.y, count)

#============================================================== Базовые классы ========================================
class BaseParticle:
    """ класс Базовая частица """
    def __init__(self, **kwargs):
        self.position = kwargs.get("position", Vector2D(0, 0))             # координаты
        self.velocity = kwargs.get("velocity", Vector2D(0, 0))             # вектор скорости
        self.acceleration = kwargs.get("acceleration", Vector2D(0, 0))     # вектор ускорения
        self.color = kwargs.get("color", (0, 0, 0))                        # цвет

    def move(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)


class BaseEmitter:
    """ класс Базовый эммитер """
    def __init__(self, **kwargs):
        self.position = kwargs.get("position",  Vector2D(0, 0))             # координаты эммитера
        self.pvelocity = kwargs.get("pvelocity",  Vector2D(1, 1))           # средняя скорость чатицы
        self.pacceleration = kwargs.get("pacceleration", Vector2D(0, 0))    # начальное ускорение частицы
        self.spread = kwargs.get("spread", math.pi / 32)                    # угол распространения
        self.pcolor = kwargs.get("pcolor", (0, 0, 0))                    # начальный цвет частиц

    def new_velocity_for_particle(self):                                    # генерирует вектор скорости для частицы
        angle = self.pvelocity.angle() + self.spread - (random.random() * 2 * self.spread)
        return Vector2D.new_vector(angle=angle, length=self.pvelocity.length())

    def emit_particle(self):
        """ Метод генерации частицы """
        return BaseParticle(position=self.position.copy(), velocity=self.new_velocity_for_particle(),
                            acceleration=self.pacceleration.copy(), color=self.pcolor)

    def init_particle(self, particle):
        """ Метод инициализации частицы,
            необходим если пользователь хочет переиспользовать
            уже ранее созданную частицу"""
        particle.position = self.position.copy()
        particle.velocity = self.new_velocity_for_particle()
        particle.acceleration = self.pacceleration.copy()
        particle.color = self.pcolor


class BaseField:
    """ класс Базовое поле взаимодействия """
    def __init__(self, **kwargs):
        self.position = kwargs.get("position", Vector2D(0, 0))
        self.mass = kwargs.get("mass", 100)

    def affect_on_particle(self, particle):                 # оказать взаимодействие на частицу
        vector = self.position - particle.position
        force = self.mass / (vector.x * vector.x + vector.y * vector.y)**1.5
        particle.acceleration += vector * force


class BaseSystemParticles:
    def __init__(self):
        self.__active_particles = []                                    # список активных частиц
        self.__inactive_particles = []                                  # список неактивных частиц
        self.__emitters = []                                            # список эммиторов системы
        self.__fields = []                                              # список полей воздействия
        self.__conditions_die = []                                      # список условий смерти частицы

    def act(self):
        self.add_particles()
        for particle in self.__active_particles:
            #particle.acceleration = Vector2D(0, 0)
            for field in self.__fields:
                field.affect_on_particle(particle)
            particle.move()
        self.kill_particles()

    def add_particles(self):                                  # добавить частицы
        for emitter in self.__emitters:
            if len(self.__inactive_particles) < 1:              # если нет неактивных
                p = emitter.emit_particle()                     # создать новую частицу
            else:
                p = self.__inactive_particles.pop(0)            # взять и преиспользовать частицу из неактивных
                emitter.init_particle(p)
            self.__active_particles.append(p)

    def kill_particles(self):                       # убить частицы, которые соответствуют условиям conditions_die
        inds = []
        for i in range(len(self.__active_particles)):
            for condition_die in self.__conditions_die:
                if condition_die(self.__active_particles[i]):
                    inds.append(i)
                    break
        for i in range(len(inds)):
            self.__inactive_particles.append(self.__active_particles.pop(inds[i] - i))

    def add_emitter(self, emitter):
        self.__emitters.append(emitter)

    def remove_emitter(self, emitter):
        self.__emitters.remove(emitter)

    def add_condition_die(self, cond):
        """Добавить условие смерти частиц.
            Пример: cond = lambda p: p.x < 0 or p.y < 0"""
        self.__conditions_die.append(cond)

    def remove_condition_die(self, cond):
        self.__conditions_die.remove(cond)

    def add_field(self, field):
        self.__fields.append(field)

    def remove_field(self, field):
        self.__fields.remove(field)

    def particles(self):
        return self.__active_particles
# ====================================================================================================================

# ==================================================== Огненные классы ===============================================
class FireParticle(BaseParticle):
    """ класс Огненная частица """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_health(kwargs.get("health", 1))
        self.set_dhealth(kwargs.get("dhealth", 1))

    def move(self):
        super().move()
        self.dec_health()

    def set_health(self, h):
        """ Метод задания начального количества
            здоровья частицы """
        if h <= 0:
            self.__health = 0
            self.__hcolor_cff = 1
        else:
            self.__health = h
            self.__hcolor_cff = self.__health / (len(FIRE_RGBS) - 1)
        self.__chg_color__()

    def set_dhealth(self, dh):
        self.__dhealth = abs(dh)

    def dec_health(self):
        self.__health -= self.__dhealth
        if self.__health < 0:
            self.__health = 0
        self.__chg_color__()

    def __chg_color__(self):
        """ Метод изменяет цвет частицы
            в зависимости от состояния её здоровья """
        self.color = FIRE_RGBS[int(self.__health / self.__hcolor_cff)]

    def health(self):
        return self.__health


class FireEmitter(BaseEmitter):
    """ класс Огненный эммитер """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pmin_health = kwargs.get("pmin_health", len(FIRE_RGBS) - 1)
        self.pmax_health = kwargs.get("pmax_health", (len(FIRE_RGBS) - 1) * 2)
        self.pmin_dhealth = kwargs.get("pmin_dhealth", 1)
        self.pmax_dhealth = kwargs.get("pmax_dhealth", 2)

    def emit_particle(self):
        return FireParticle(position=self.position.copy(), velocity=self.new_velocity_for_particle(),
                            acceleration=self.pacceleration.copy(),
                            health=random.randint(self.pmin_health, self.pmax_health),
                            dhealth=random.randint(self.pmin_dhealth, self.pmax_dhealth))

    def init_particle(self, particle):
        """ Метод инициализации частицы,
            необходим если пользователь хочет переиспользовать
            уже ранее созданную частицу"""
        particle.position = self.position.copy()
        particle.velocity = self.new_velocity_for_particle()
        particle.acceleration = self.pacceleration.copy()
        particle.set_health(random.randint(self.pmin_health, self.pmax_health))
        particle.set_dhealth(random.randint(self.pmin_dhealth, self.pmax_dhealth))
# ====================================================================================================================

# ================================================ L-System ==========================================================
class LSystem:
    """ Класс L-Система, позволяет генерировать фрактальные текстовые последовательности """
    def __init__(self, **kwargs):
        self.__axiom = kwargs.get("sentence", "")               # аксиома, начальное состояние системы
        self.__sentence = self.__axiom                          # пример, текущее состояние системы
        self.rules = kwargs.get("rules", {})                    # правила системы

    def append_rule(self, rule):
        self.rules[rule[0]] = rule[1]

    def remove_rule(self, rule_key):
        self.rules.pop(rule_key)

    def next_state(self):
        """ перевести систему в следующее состояние"""
        generate = ""
        for key in self.__sentence:
            val = self.rules.get(key, key)       # отобразить символ примера в последовательность с помощью правила
            generate += val
        self.__sentence = generate

    def state(self):                             # состояние системы
        return self.__sentence

    def axiom(self):
        return self.__axiom

    def first_state(self):
        """ перевести систему в начальное состояние"""
        self.__sentence = self.__axiom
# ====================================================================================================================

# =================================================== Исполнители, рисовальщики ======================================
class Turtle:
    """ Класс Черепашка, объект исполняющий команды рисования """
    def __init__(self, px_handle, size, **kwargs):
        self.__size = size                                                    # размер холста
        self.__px_handle = px_handle                                          # контекст холста
        self.set_position(kwargs.get("position", Vector2D(0, 0)))             # установить начальную позицию черепахи
        self.__line_color = kwargs.get("line_color", (0, 0, 0))               # цвет линии
        self.velocity = Vector2D(kwargs.get("count_steps", -1), 0)            # вектор скорости черепахи,
                                                                              # от него зависит сколько пиксельных шагов
                                                                              # сделает черепаха при команде move
        self.set_angle_rotate(kwargs.get("angle_rotate", math.pi / 2))        # угол поворота черепахи
        self.__commands = {}                                                  # словарь команд, значениями данного
                                                                              # словаря должны быть указатели на методы
                                                                              # данного класса без self
                                                                              # Например: {'M': Turtle.move, ...}

    def set_px_handle(self, px_handle):
        self.__px_handle = px_handle

    def check_position(self, pos)-> bool:
        """ Метод проверка нахождения позиции вне холста"""
        return pos.x < 0 or pos.x >= self.__size[0] or pos.y < 0 or pos.y >= self.__size[1]

    def set_position(self, pos):
        """ Метод, изменить позицию черепахи на холсте """
        if self.check_position(pos):
            raise ValueError("Uncorrect position!!!")
        self.__position = pos

    def position(self):
        return self.__position

    def move(self):
        """ Метод, передвинуть черепаху и нарисовать линию"""
        p = self.__position + self.velocity
        p.round_xy()
        if self.check_position(p):
            raise ValueError("Uncorrect position!!!")
        draw_line(self.__px_handle, self.__position.x, self.__position.y, p.x, p.y, self.__line_color)
        self.__position = p

    def empty_move(self):
        """ Метод, передвинуть черепаху, но не рисовать линию"""
        p = self.__position + self.velocity
        p.round_xy()
        if self.check_position(p):
            raise ValueError("Uncorrect position!!!")
        self.__position = p

    def rotate(self, angle):
        self.velocity = Vector2D.new_vector(length=self.velocity.length(), angle=angle + self.velocity.angle())

    def set_angle_rotate(self, angle):
        """ Метод изменения угла поворота черепахи """
        self.__angle = angle

    def rotate_left(self):
        """ повернуть влево на ранее заданный угол """
        self.rotate(-self.__angle)

    def rotate_right(self):
        """ повернуть вправо на ранее заданный угол """
        self.rotate(self.__angle)

    def set_count_steps(self, steps):
        """ изменить количество пиксельных шагов """
        self.velocity = Vector2D.new_vector(length=steps, angle=self.velocity.angle())

    def set_commands(self, commands):
        self.__commands = commands

    def append_command(self, command, act_func):
        """ добавить команду """
        self.__commands[command] = act_func

    def remove_command(self, command):
        """ убрать команду  """
        self.__commands.pop(command)

    def run_command(self, command):
        """ исполнить команду """
        f = self.__commands.get(command)            # получить указатель на метод
        if f:
            f(self)                                 # выполнить метод

    def set_line_color(self, color):
        self.__line_color = color

    def line_color(self):
        return self.__line_color


class LSystemDrawExecutor(Turtle):
    """ Класс который отображает состояние L-системы в рисунок"""
    def __init__(self, px_handle, size, **kwargs):
        super().__init__(px_handle, size, **kwargs)
        self.__lsystem = kwargs.get('lsystem')

    def lsystem(self):
        return self.__lsystem

    def set_lsystem(self, lsystem):
        self.__lsystem = lsystem

    def execute_lsystem_state(self):
        """ выполнить состояние L-системы, как последовательность комманд """
        if self.__lsystem is None:
            raise ValueError("None lsystem pointer!!!")
        state = self.__lsystem.state()
        for command in state:
            self.run_command(command)
# ====================================================================================================================

def draw_fill_square(px_handle, size, x1: int, y1: int, x2: int, y2: int,color = (0, 0, 0)):
    if x1 >= 0 and x2 < size[0] and y1 >= 0 and y2 < size[1]:
        for x in range(x1, x2):
            draw_line(px_handle, x, y1, x, y2, color)


def draw_particles(px_handle, size, particles, d_particle = 5):
    """ Отобразить частицы
        d_particle - диамметр частицы """
    for particle in particles:
        x1 = int(particle.position.x - d_particle)
        x2 = int(particle.position.x + d_particle)
        y1 = int(particle.position.y - d_particle)
        y2 = int(particle.position.y + d_particle)
        draw_fill_square(px_handle, size, x1, y1, x2, y2, particle.color)


class ParticlesFractalDrawer(LSystemDrawExecutor):
    def __init__(self, px_handle, size, **kwargs):
        super().__init__(px_handle, size, **kwargs)
        self.particles = kwargs.get("particles", [])
        self.d_particle = kwargs.get("diameter_particle", 1)

    def move(self):
        p = self._Turtle__position + self.velocity
        for particle in self.particles:
            pos = self._Turtle__position.copy()
            pos.x = particle.position.x + pos.x * random.random()
            pos.y = particle.position.y + pos.y * random.random()
            draw_fill_square(self._Turtle__px_handle, self._Turtle__size,
                             int(pos.x - self.d_particle), int(pos.y - self.d_particle),
                             int(pos.x + self.d_particle), int(pos.y + self.d_particle), particle.color)
        self._Turtle__position = p


class MainWindow(Frame):
    def __init__(self, parent):
        """constructor, init main elements"""
        super().__init__(parent)

        self.img = None
        self.tk_img = None
        self.points = []
        self.main_stroke_color = (0, 0, 0)
        self.main_point_color = (255, 0, 0)

        self.system_particles = None
        self.lsystem = None
        self.lsys_drawer = None

        self.init_lsystem()

        self.parent = parent
        self.initUi()


    def initUi(self):
        """method, create all window's elements. It is create User Interface"""
        self.parent.title('Огонь')                       # setting window title
        self.centerWindow()                                     # setting position window in monitor's center
        self.parent.resizable(False, False)
        self.pack(fill=BOTH, expand=1)                          # pack window

        self.display_panel = Frame(self)                        # draw panel

        self.canvas = Canvas(self.display_panel, bd=0, highlightthickness=1, highlightbackground="blue", bg="black")
        self.canvas.place(relx = 0, rely = 0, relwidth=1, relheight=1)

        self.display_panel.pack(fill=BOTH, expand=1, padx=5, pady=5)
        self.parent.after(500, self.loop_system_particles)


    def centerWindow(self):
        """method who setting position window on monitor's center"""
        self.w = 800
        self.h = 500
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        self.x = int((sw - self.w) / 2)
        self.y = int((sh - self.h) / 2)
        self.parent.geometry(f'{self.w}x{self.h}+{self.x}+{self.y}')


    def init_lsystem(self):
        if self.lsystem is None:
            self.lsystem = LSystem(sentence='F-G-G', rules={'F': 'F-G+F+G-F', 'G': 'GG'})
            self.lsystem_iterations = 1
            for i in range(self.lsystem_iterations):
                self.lsystem.next_state()        # перевести L-систему в состояние i


    def init_lsys_drawer(self, px_handle):
        if self.lsys_drawer is None:
            self.lsys_drawer_min_len = 10
            self.lsys_drawer = ParticlesFractalDrawer(None, self.img.size,
                                 count_steps=self.lsys_drawer_min_len,
                                 angle_rotate=2 * math.pi / 3, lsystem=self.lsystem, diameter_particle=2)
            self.lsys_drawer.set_commands({'F': ParticlesFractalDrawer.move, 'G': ParticlesFractalDrawer.move,
                                           '+': ParticlesFractalDrawer.rotate_right, '-': ParticlesFractalDrawer.rotate_left})
            self.start_lsys_drawer_velocity = self.lsys_drawer.velocity.copy()
            self.start_lsys_drawer_position = self.lsys_drawer.position().copy()
        self.lsys_drawer.set_px_handle(px_handle)


    def init_system_particles(self):
        if self.system_particles is None:
            size = (self.canvas.winfo_width(), self.canvas.winfo_height())
            self.system_particles = BaseSystemParticles()

            a = self.lsys_drawer_min_len * 2 ** self.lsystem_iterations     # сторона треугольника
            r = a * 3 ** 0.5 / 6                                            # радиус вписанной окружности

            for j in range(size[0] // 2 - size[0] // 8 , size[0] // 2 + size[0] // 8, 5):
                pos_c = Vector2D(j, size[1] - 100)
                p = 1 - abs(size[0] // 2 - j) * 8 / size[0]
                self.system_particles.add_emitter(FireEmitter(position=Vector2D(pos_c.x - a / 2, pos_c.y + r),
                                                              pvelocity=Vector2D(0, -7),
                                                              pmin_health=0,
                                                              pmax_health=int(len(FIRE_RGBS) * p)))

            self.system_particles.add_condition_die(lambda p: p.position.x < 0 or p.position.y < 0 or\
                                                              p.position.x >= size[0] or p.position.y >= size[1])
            self.system_particles.add_condition_die(lambda p: p.health() == 0)


    def loop_system_particles(self):
        size = (self.canvas.winfo_width(), self.canvas.winfo_height())  # define size canvas
        self.img = Image.new('RGB', size, "black")

        px_handle = self.img.load()
        self.init_lsys_drawer(px_handle)

        self.init_system_particles()
        self.system_particles.act()

        self.lsys_drawer.set_position(self.start_lsys_drawer_position.copy())
        self.lsys_drawer.velocity = self.start_lsys_drawer_velocity.copy()
        self.lsys_drawer.particles = self.system_particles.particles()
        self.lsys_drawer.execute_lsystem_state()

        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=NW)
        self.parent.after(50, self.loop_system_particles)


def main():
    """main programm function"""
    root = Tk()                                 # create TK
    main_window = MainWindow(root)              # create Frame Window on TK
    root.mainloop()                             # run mainloop


if __name__ == "__main__":
    main()
