import time
from functools import wraps

from flask import (
    Flask,
    request,
    flash,
    redirect,
    url_for,
)


class DuplicateTransition(Exception):
    """Basic exc."""


class InvalidTransition(Exception):
    """Basic exc."""


class StateMachine(object):
    """State machine as intuitively as possible."""

    def __init__(self, transitions):
        """States."""
        self.transitions = transitions
        self.states = set()
        for transition in self.transitions:
            self.states.update(transition)
        self.history = []

    def __repr__(self):
        """Representation of FSM."""
        return ('StateMachine(states={states}, '
                'transitions={tns}, history={history})').format(
            states=self.states,
            tns=self.transitions,
            history=self.history,
        )

    @property
    def current(self, to=None):
        """Get current state 2-tuple."""
        if to is not None:
            fromstate = request.url_rule.endpoint
            current = (fromstate, to)
            return current

    def has_not_skipped(self, to=None):
        """Determine if any transition was skipped."""
        current = self.current
        if current is None:
            return True
        idx = self.transitions.index(current)
        for i, state in enumerate(self.transitions):
            if i == idx:
                break
            if state not in self.history:
                return False
        return True

    def can_transition(self, to=None):
        """Determine if we can transition."""
        fromstate = request.url_rule.endpoint
        current = (fromstate, to)
        return all([
            current in self.transitions,
            current not in self.history,
            self.has_not_skipped(to=to),
        ])

    def transition(self, to=None):
        """Keep a record of transition history."""
        if to is not None:
            fromstate = request.url_rule.endpoint
            # Ensure it's in the list of acceptable states
            # but NOT in the ones we've already seen
            current = (fromstate, to)
            if current not in self.transitions:
                raise InvalidTransition('{} -> {}'.format(*current))
            if current in self.history:
                raise DuplicateTransition('{} -> {}'.format(*current))
            self.history.append(current)

    def complete(self, state):
        """Determine if FSM is complete and should be reset."""
        return True

    @property
    def status(self):
        """Draw out current status."""
        return '\n'.join([
            '{} -> {}'.format(fromval, to) for
            (fromval, to) in self.history
        ])

    def check(self, accept=[], to=[]):
        """The core checker. Determines if a current route can access next."""
        def wrapper(func, *args):
            @wraps(func)
            def _inner(*args):
                next = request.args.get('to')
                # curr = self.get_current
                # if next not in to and next is not None:
                #     raise InvalidTransition(
                #         'Cannot transition to "{}" from "{}". '
                #         'Available transitions: {}'.format(
                #             next, func.__name__, to
                #         )
                #     )
                # if next is not None:
                #     self.transition(curr, next)
                return func(*args)
            return _inner
        return wrapper


fsm = StateMachine([
    ('index', 'a'),
    ('a', 'b'),
    ('b', 'index'),
    ('b', 'c'),
])

app = Flask('fsm-app')
app.config['SECRET_KEY'] = '1234ok'


@app.route('/')
@fsm.check(accept=['b'], to=['a', 'b'])
def index():
    has_step = request.args.get('to')
    if has_step is not None:
        time.sleep(2)
        flash('Did some stuff... going to A')
        fsm.transition(to='a')
        return redirect(url_for('a'))
    return 'Hello from INDEX. {}'.format(repr(fsm))


@app.route('/a', methods=['GET', 'POST'])
@fsm.check(accept=['b'], to=['a', 'b'])
def a():
    if request.method == 'POST':
        time.sleep(2)
        flash('Did some stuff... going to B')
        fsm.transition(to='b')
        return redirect(url_for('b'))
    if fsm.can_transition(to='b'):
        return '<form method="POST" action="/a">A form<input type="text" name="to"><button>GO</button></form>'
    else:
        flash('Redirect to B after successfully doing xtion')
        return redirect(url_for('b'))


@app.route('/b', methods=['GET', 'POST'])
@fsm.check(accept=['b'], to=['a', 'b'])
def b():
    if request.method == 'POST':
        time.sleep(2)
        flash('Did some stuff... going to B')
        fsm.transition(to='index')
        return redirect(url_for('index'))
    if fsm.can_transition(to='index'):
        return '<form method="POST" action="/b">B form<input type="text" name="to"><button>GO</button></form>'
    else:
        # flash('Redirect to B after successfully doing xtion')
        # return redirect(url_for('b'))
        return 'states we\'ve been to: \n' + fsm.status


@app.route('/c')
def c():
    return 'Hello from C'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
