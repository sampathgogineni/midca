from _plan.pyhop121 import pyhop, methods, operators
import plans

class PyHopPlanner:
	
	'''
	MIDCA module that implements a python version of the SHOP hierarchical task network (HTN) planner. HTN planners require a set of user-defined methods to generate plans; these are defined in the methods python module and declared in the constructor for this class.
	Note that this module uses has several methods to translate between MIDCA's world and goal representations and those used by pyhop; these should be changed if a new domain is introduced.
	'''
	
	def __init__(self):
		#declares pyhop methods. This is where the planner should be given the domain information it needs.
		methods.declare_methods()
	
	def init(self, world, mem):
		self.mem = mem
		#load operators from world. Note that using this simple method MIDCA will not check the types or values of arguments, though it will check for plan validity.
		#Also, this method depends on the default MIDCA world simulator.
		self.operators = {op.name: plans.Operator(op.name, op.objNames) for op in world.operators.values()}
	
	#this will require a lot more error handling, but ignoring now for debugging.
	def run(self, cycle, verbose = 2):
		world = self.mem.get(self.mem.STATES)[-1]
		goals = self.mem.get(self.mem.CURRENT_GOALS)
		if not goals:
			if verbose >= 2:
				print "No goals received by planner. Skipping planning."
			return
		try:
			plan = self.mem.get(self.mem.GOAL_GRAPH).getPlan(goals)
		except AttributeError:
			plan = None
		if plan:
			if verbose >= 2:
				print "Old plan retrieved. Checking validity...",
			valid = world.plan_correct(plan)
			if not valid:
				plan = None 
				#if plan modification is added to MIDCA, do it here.
				if verbose >= 2:
					print "invalid."
			elif verbose >= 2:
				print "valid."
		
		#ensure goals is a collection to simplify things later.
		if not isinstance(goals, collections.Iterable):
			goals = [goals]
		
		if not plan:
			#use pyhop to generate new plan
			if verbose >= 2:
				print "Planning..."
			try:
				pyhopState = pyhop_state_from_world(world)
			except Exception:
				raise ValueError("Could not generate a valid pyhop state from current world state")
			try:
				pyhopTasks = pyhop_tasks_from_goals(goals)
			except Exception:
				raise ValueError("Could not generate a valid pyhop goal set from current goals")
			try:
				pyhopPlan = pyhop.pyhop(pyhopState, pyhopTasks, verbose = 0)
			except Exception:
				pyhopPlan = None
			if not pyhopPlan:
				if verbose >= 1:
					print "Planning failed for ",
					for goal in goals:
						print goal, " ",
					print
				return
			#change from pyhop plan to MIDCA plan
			midcaPlan = plans.Plan([plans.Action(self.operators[action[0]], list(action[1:])) for action in pyhopPlan], goals)
			
			if verbose >= 1:
				print "Planning complete."
			if verbose >= 2:
				print "Plan: ",
				for step in plan:
					print str(step),
				print
			#save new plan
			if plan:
				self.mem.get(self.mem.GOAL_GRAPH).addPlan(plan)

	def pyhop_state_from_world(self, world, name = "state"):
		s = pyhop.State(name)
		s.pos = {}
		s.clear = {}
		s.holding = False
		s.fire = {}
		s.free = {}
		blocks = []
		for objname in world.objects:
			if world.objects[objname].type.name == "BLOCK" and objname != "table":
				blocks.append(objname)
			elif world.objects[objname].type.name == "ARSONIST":
				s.free[objname] = False
		for atom in world.atoms:
			if atom.predicate.name == "clear":
				s.clear[atom.args[0].name] = True
			elif atom.predicate.name == "holding":
				s.holding = atom.args[0].name
			elif atom.predicate.name == "arm-empty":
				s.holding = False
			elif atom.predicate.name == "on":
				s.pos[atom.args[0].name] = atom.args[1].name
			elif atom.predicate.name == "on-table":
				s.pos[atom.args[0].name] = "table"
			elif atom.predicate.name == "onfire":
				s.fire[atom.args[0].name] = True
			elif atom.predicate.name == "free":
				s.free[atom.args[0].name] = True
		for block in blocks:
			if block not in s.clear:
				s.clear[block] = False
			if block not in s.fire:
				s.fire[block] = False
			if block not in s.pos:
				s.pos[block] = "in-arm"
		return s
	
	#note: str(arg) must evaluate to the name of the arg in the world representation for this method to work.
	def pyhop_tasks_from_goals(self, goals):
		alltasks = []
		blkgoals = pyhop.Goal("goals")
		blkgoals.pos = {}
		for goal in goals:
			#extract predicate
			if 'predicate' in goal.kwargs:
				predicate = str(goal.kwargs['predicate'])
			elif 'Predicate' in goal.kwargs:
				predicate = str(goal.kwargs['Predicate'])
			elif goal.args:
				predicate = str(goal.args[0])
			else:
				raise ValueError("Goal " + str(goal) + " does not translate to a valid pyhop task")
			args = [str(arg) for arg in goal.args]
			if args[0] == predicate:
				args.pop(0)
			if predicate == "on":
				blkgoals.pos[args[0]] = args[1]
			elif predicate == "onfire" and goal['negate'] == True:
				alltasks.append(("put_out", args[0]))
			elif goal.predicate == "free" and goal['negate'] == True:
				alltasks.append(("catch_arsonist", args[0]))
		if blkgoals.pos:
			alltasks.append(("move_blocks", blkgoals))
		return alltasks	
	
	