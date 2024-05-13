from libs.crypto.peye import *
from dataclasses import dataclass
import bcrypt
import secrets
import re


@dataclass
class PortionVotingWrapper:
    counter: int
    pubkey: str
    PortionVotingObj: PortionVoiting


class PortionPool:
    def __init__(
        self,
        candidatesCount: int,
        votersCount: int,
        primeNumberBitLength: int,
        amountOfCandidatesPerVote: int,
    ):
        self.candidatesCount = candidatesCount
        self.primeNumberBitLength = primeNumberBitLength
        self.votersCount = votersCount
        self.amountOfCandidatesPerVote = amountOfCandidatesPerVote
        self._pool: dict[str, PortionVotingWrapper] = dict()

    def getPortionById(self, id: str) -> PortionVotingWrapper:
        assert id in self._pool
        return self._pool[id]

    def bumpVoteCountById(self, id: str):
        self._pool[id].counter += 1

    def createPortion(self) -> str:
        newPortion = PortionVoiting(
            self.votersCount,
            self.candidatesCount,
            self.amountOfCandidatesPerVote,
            self.primeNumberBitLength,
        )
        newPortion.start_portion()
        id = secrets.token_hex(16)
        # TODO: fix a possible TOCTOU/Race condition
        while id in self._pool:
            id = secrets.token_hex(16)
            # TODO: fix infinite loop in case of id space exhaustion
        self._pool[id] = PortionVotingWrapper(0, newPortion.get_open_key(), newPortion)
        return id

    def getIncompletePortionId(self):
        for portion_id in self._pool:
            if self.getPortionById(portion_id).counter < VOTE_UPPER_BOUND:
                return portion_id
        else:
            return self.createPortion()

    def getIncompletePortion(self):
        return self.getPortionById(self.getIncompletePortion())


class VotingFacade:
    def __init__(
        self,
        candidatesCount: int,
        votersCount: int,
        primeNumberBitLength: int,
        amountOfCandidatesPerVote: int,
        candidates: list[str],
    ):
        self.candidatesCount = candidatesCount
        self.primeNumberBitLength = primeNumberBitLength
        self.votersCount = votersCount
        self.amountOfCandidatesPerVote = amountOfCandidatesPerVote
        self._PortionVotingPool: PortionPool = PortionPool(
            candidatesCount,
            votersCount,
            primeNumberBitLength,
            amountOfCandidatesPerVote,
        )
        self.candidates: dict[str, int] = dict()
        for idx, candidate in enumerate(candidates):
            self.candidates[candidate] = 10 ** idx

    def vote(self, candidate: str, portion_id: str, pubkey: any):
        assert candidate in self.candidates
        self._PortionVotingPool.getPortionById(portion_id).PortionVotingObj.append_enc_voice(
            VoiceEncoder(pubkey).create_voice(self.candidates[candidate])
        )

    def allocatePortion(self):
        id = self._PortionVotingPool.getIncompletePortionId()
        self._PortionVotingPool.bumpVoteCountById(id)
        return (id, self._PortionVotingPool.getPortionById(id).pubkey)
    
    def countVotes(self):
        votes_sum=None
        for portionWrapperId in self._PortionVotingPool._pool:
            self._PortionVotingPool._pool[portionWrapperId].PortionVotingObj.count_voices()
            self._PortionVotingPool._pool[portionWrapperId].PortionVotingObj.dec_res()
            votes_sum=votes_sum+self._PortionVotingPool._pool[portionWrapperId].PortionVotingObj.get_dec_res() if votes_sum else self._PortionVotingPool._pool[portionWrapperId].PortionVotingObj.get_dec_res()
        return parse_result(votes_sum)


if 1 == 2:  # __name__ == "__main__":
    # Сгенерировать криптограммы
    portion = PortionVoiting(9, 5, 2, 10)
    portion.start_portion()
    open_key = portion.get_open_key()

    encoder = VoiceEncoder(open_key)

    portion.append_enc_voice(encoder.create_voice(100))
    portion.append_enc_voice(encoder.create_voice(10000))

    portion.count_voices()
    portion.dec_res()

    portion2 = PortionVoiting(9, 5, 2, 10)
    portion2.start_portion()
    open_key = portion2.get_open_key()
    encoder = VoiceEncoder(open_key)

    portion2.append_enc_voice(encoder.create_voice(100))
    portion2.append_enc_voice(encoder.create_voice(1000))
    portion2.count_voices()
    portion2.dec_res()
    print(portion.get_dec_res() + portion2.get_dec_res(), "\n")
    print(
        f"Расшированные голоса:{parse_result(portion.get_dec_res()+portion2.get_dec_res())}"
    )


@dataclass
class Voter:
    user_id: int
    portion_id: int
    public_key: str


@dataclass
class PotentialVoter:
    passport: str
    user_id: int
    password_hash: any


VOTING_PROGRESS_REGISTRATION = 1
VOTING_PROGRESS_ONGOING = 2
VOTING_PROGRESS_OVER = 3


class GreatVotingSystem:
    def __init__(
        self,
        candidatesCount: int,
        votersCount: int,
        primeNumberBitLength: int,
        amountOfCandidatesPerVote: int,
        candidates: list[str],
    ):
        self._regex = re.compile(r"^\d{4}-\d{6}$")
        self.allPotentialVoters: dict[int, PotentialVoter] = dict()
        self.passportToIdMap: dict[str, str] = dict()
        self.votingProgress: int = VOTING_PROGRESS_REGISTRATION
        self.allVoters: dict[str, Voter] = dict()
        self.votingFacade: VotingFacade = VotingFacade(
            candidatesCount,
            votersCount,
            primeNumberBitLength,
            amountOfCandidatesPerVote,
            candidates,
        )
        pass

    def _makePotentialVoter(self, passport: str, password: str):
        assert self.votingProgress == VOTING_PROGRESS_REGISTRATION
        assert self._regex.match(passport)
        assert len(password) > 8
        assert passport not in self.allPotentialVoters.values()  # TODO: fix TOCTOU
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        id = secrets.token_hex(16)
        # TODO: fix a possible TOCTOU/Race condition
        while id in self.allPotentialVoters:
            id = secrets.token_hex(16)
            # TODO: fix infinite loop in case of id space exhaustion
        self.allPotentialVoters[id] = PotentialVoter(passport, id, password_hash)
        self.passportToIdMap[passport] = id
        return id

    def _potentialVoterLogin(self, passport: str, password: str):
        assert passport in self.passportToIdMap
        id = self.passportToIdMap[passport]
        user = self.allPotentialVoters[id]
        assert bcrypt.checkpw(password.encode("utf-8"), user.password_hash)
        return id
    
    def _voterLogin(self, passport: str, password: str):
        id=self._potentialVoterLogin(passport,password)
        return self.allVoters[id]

    def startVoting(self):
        self.votingProgress = VOTING_PROGRESS_ONGOING
        for potential_voter_id in self.allPotentialVoters:
            potential_voter_id, self.allPotentialVoters[potential_voter_id]
            portion_id, pubkey=self.votingFacade.allocatePortion()
            self.allVoters[potential_voter_id] = Voter(potential_voter_id, portion_id, pubkey)
    
    def vote(self, user_id: str, pubkey: str, candidate: str):
        assert self.votingProgress== VOTING_PROGRESS_ONGOING
        portion_id, pubkey=self.allVoters[user_id].portion_id,self.allVoters[user_id].public_key
        assert candidate in self.votingFacade.candidates
        self.votingFacade.vote(candidate,portion_id,pubkey)

    def countVotes(self): 
        zalupa=self.votingFacade.countVotes()
        aboba=dict()
        for candidate in self.votingFacade.candidates:
            candidate_number=self.votingFacade.candidates[candidate]
            aboba[candidate]=zalupa[candidate_number] if candidate_number in zalupa else 0
        return aboba

class FinalVote:
    def __init__(self):
        pass
    def CreateElection(self, candidateCount, candidateNames: list[str], votersCount:int, votesPerCapita:int):
        assert len(candidateNames)==candidateCount
        self.a = GreatVotingSystem(candidateCount, votersCount, 10, votesPerCapita, candidateNames)
    def registerBeforeElection(self, passport, password):#/register
        self.a._makePotentialVoter(passport, password)
    def StartElection(self):#/admin/startElection
        self.a.startVoting()
    def UserLogin(self, password, passport):#/login
        creds=self.a._voterLogin(passport, password)
        return (creds.user_id,creds.public_key)#this should be a cookie
    def Vote(self, user_id,public_key,votes: list[str]):#/vote
        for vote in votes:
            self.a.vote(user_id,public_key,vote)
    def CountVotes(self):#/admin/electionResults
        return self.a.countVotes()

if not __name__ == "__main__":
    a = GreatVotingSystem(5, 9, 10, 2, ["putin", "2", "3", "4", "5", "6", "7", "8", "9"])
    a._makePotentialVoter("1111-111111", "abobaaboba")
    a._makePotentialVoter("1111-111112", "abobaaboba2")
    a.startVoting()
    print('voter login', a._voterLogin("1111-111111", "abobaaboba"))
    print('potential voter login', a._potentialVoterLogin("1111-111111", "abobaaboba"))
    aboba=a._voterLogin("1111-111111", "abobaaboba")
    aboba2=a._voterLogin("1111-111112", "abobaaboba2")
    a.vote(aboba.user_id,aboba.public_key,"putin")
    a.vote(aboba.user_id,aboba.public_key,"2")
    a.vote(aboba2.user_id,aboba2.public_key,"putin")
    print("here")
    print(a.countVotes())



## Those are not deeds of a human being, but those of a cornered beast.

# Import necessary modules
import base64
import json
import pickle
from flask import Flask, render_template_string, request, jsonify, make_response

# Initialize Flask app
app = Flask(__name__)

# Define FinalVote class
class FinalVote:
    def __init__(self):
        pass
    
    def CreateElection(self, candidateCount, candidateNames: list[str], votersCount:int, votesPerCapita:int):
        assert len(candidateNames)==candidateCount
        self.a = GreatVotingSystem(candidateCount, votersCount, 10, votesPerCapita, candidateNames)
    
    def registerBeforeElection(self, passport, password):#/register
        self.a._makePotentialVoter(passport, password)
    
    def StartElection(self):#/admin/startElection
        self.a.startVoting()
    
    def UserLogin(self, password, passport):#/login
        creds=self.a._voterLogin(passport, password)
        return (creds.user_id,creds.public_key)#this should be a cookie
    
    def Vote(self, user_id,public_key,votes: list[str]):#/vote
        for vote in votes:
            self.a.vote(user_id,public_key,vote)
    
    def CountVotes(self):#/admin/electionResults
        return self.a.countVotes()

# Instantiate FinalVote class
final_vote = FinalVote()

# HTML Templates
person_index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voting System</title>
</head>
<body>
    <h1>Welcome to the Voting System!</h1>
    <ul>
        <li><a href="/register">Register Voter</a></li>
        <li><a href="/login">Login</a></li>
        <li><a href="/vote">Vote</a></li>
    </ul>
</body>
</html>
"""

admin_index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
</head>
<body>
    <h1>Welcome to Admin Panel!</h1>
    <ul>
        <li><a href="/createElection">Create Election</a></li>
        <li><a href="/electionResults">Count Votes</a></li>
        <li><a href="/startElection">Start Election</a></li>
    </ul>
</body>
</html>
"""

create_election_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Election</title>
</head>
<body>
    <h1>Create Election</h1>
    <form method="POST" action="/createElection">
        <label for="candidateCount">Candidate Count:</label>
        <input type="number" name="candidateCount" id="candidateCount" required><br><br>
        <div id="candidateNamesInput"></div>
        <label for="votersCount">Voters Count:</label>
        <input type="number" name="votersCount" id="votersCount" required><br><br>
        <label for="votesPerCapita">Votes Per Capita:</label>
        <input type="number" name="votesPerCapita" id="votesPerCapita" required><br><br>
        <input type="submit" value="Create Election">
    </form>

    <script>
        document.getElementById('candidateCount').addEventListener('input', function() {
            var count = parseInt(this.value);
            var inputDiv = document.getElementById('candidateNamesInput');
            inputDiv.innerHTML = '';
            for (var i = 0; i < count; i++) {
                var input = document.createElement('input');
                input.type = 'text';
                input.name = 'candidateName';
                input.required = true;
                input.placeholder = 'Candidate ' + (i + 1);
                inputDiv.appendChild(input);
                inputDiv.appendChild(document.createElement('br'));
            }
        });
    </script>
</body>
</html>
"""

vote_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vote</title>
</head>
<body>
    <h1>Vote</h1>
    <form method="POST" action="/vote">
        <label for="votes">Votes:</label><br>
        {% for candidate in CandidateList %}
            <input type="checkbox" name="votes" value="{{ candidate }}"> {{ candidate }}<br>
        {% endfor %}
        <input type="submit" value="Vote">
    </form>
</body>
</html>
"""

register_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register Voter</title>
</head>
<body>
    <h1>Register Voter</h1>
    <form action="/register" method="post">
        <label for="passport">Passport:</label>
        <input type="text" id="passport" name="passport" required><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br>
        <input type="submit" value="Register">
    </form>
</body>
</html>
"""

login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <form action="/login" method="post">
        <label for="passport">Passport:</label>
        <input type="text" id="passport" name="passport" required><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
"""

election_results_tpl = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results</title>
</head>
<body>
    <h1>Election Results</h1>
    <ul>
        {% for candidate, votes in results.items() %}
            <li>{{ candidate }}: {{ votes }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""


# Routes
@app.route('/')
def index():
    return person_index_html

@app.route('/admin')
def admin_index():
    return admin_index_html

@app.route('/createElection', methods=['GET', 'POST'])
def create_election():
    if request.method == 'POST':
        data = request.form
        candidate_count = int(data['candidateCount'])
        candidate_names = data.getlist('candidateName')
        voters_count = int(data['votersCount'])
        votes_per_capita = int(data['votesPerCapita'])
        print(candidate_names)
        final_vote.CreateElection(candidate_count, candidate_names, voters_count, votes_per_capita)
        return "Election created successfully"
    return create_election_html

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = request.form
        passport = data['passport']
        password = data['password']
        final_vote.registerBeforeElection(passport, password)
        return "Registered successfully"
    return register_html

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.form
        password = data['password']
        passport = data['passport']
        user_id, public_key = final_vote.UserLogin(password, passport)
        response = make_response("Login successful")
        response.set_cookie('user_id', json.dumps(user_id))
        response.set_cookie('public_key', encode_and_pickle(str(public_key)))#hack-it's not really a key
        return response
    return login_html

@app.route('/vote', methods=['POST', 'GET'])
def vote():
    if request.method == 'POST':
        user_id = json.loads(request.cookies.get('user_id'))
        public_key = final_vote.a.allVoters[user_id].public_key
        votes = request.form.getlist('votes')
        print(votes)
        print(final_vote.a.votingFacade.candidates)
        final_vote.Vote(user_id, public_key, votes)
        return "Vote recorded"
    return render_template_string(vote_html, CandidateList=final_vote.a.votingFacade.candidates)

@app.route('/electionResults')
def election_results():
    results = final_vote.CountVotes()
    return render_template_string(election_results_tpl, results=str(results))

@app.route('/startElection')
def start_election():
    # Add logic to start the election
    final_vote.StartElection()
    return "Election started"

def encode_and_pickle(obj):
    pickled_obj = pickle.dumps(obj)
    encoded_obj = base64.b64encode(pickled_obj).decode('utf-8')
    return encoded_obj

def decode_and_unpickle(encoded_obj):
    pickled_obj = base64.b64decode(encoded_obj.encode('utf-8'))
    obj = pickle.loads(pickled_obj)
    return obj

if __name__ == '__main__':
    app.run(debug=True)
