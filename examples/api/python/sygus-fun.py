#!/usr/bin/env python
###############################################################################
# Top contributors (to current version):
#   Yoni Zohar, Andres Noetzli, Mudathir Mohamed
#
# This file is part of the cvc5 project.
#
# Copyright (c) 2009-2021 by the authors listed in the file AUTHORS
# in the top-level source directory and their institutional affiliations.
# All rights reserved.  See the file COPYING in the top-level source
# directory for licensing information.
# #############################################################################
#
# A simple demonstration of the solving capabilities of the cvc5 sygus solver
# through the Python API. This is a direct translation of sygus-fun.cpp.
##

import copy
import cvc5
import utils
from cvc5 import Kind

if __name__ == "__main__":
  slv = cvc5.Solver()

  # required options
  slv.setOption("sygus", "true")
  slv.setOption("incremental", "false")

  # set the logic
  slv.setLogic("LIA")

  integer = slv.getIntegerSort()
  boolean = slv.getBooleanSort()

  # declare input variables for the functions-to-synthesize
  x = slv.mkVar(integer, "x")
  y = slv.mkVar(integer, "y")

  # declare the grammar non-terminals
  start = slv.mkVar(integer, "Start")
  start_bool = slv.mkVar(boolean, "StartBool")

  # define the rules
  zero = slv.mkInteger(0)
  one = slv.mkInteger(1)

  plus = slv.mkTerm(Kind.Add, start, start)
  minus = slv.mkTerm(Kind.Sub, start, start)
  ite = slv.mkTerm(Kind.Ite, start_bool, start, start)

  And = slv.mkTerm(Kind.And, start_bool, start_bool)
  Not = slv.mkTerm(Kind.Not, start_bool)
  leq = slv.mkTerm(Kind.Leq, start, start)

  # create the grammar object
  g = slv.mkSygusGrammar([x, y], [start, start_bool])

  # bind each non-terminal to its rules
  g.addRules(start, {zero, one, x, y, plus, minus, ite})
  g.addRules(start_bool, {And, Not, leq})

  # declare the functions-to-synthesize. Optionally, provide the grammar
  # constraints
  max = slv.synthFun("max", [x, y], integer, g)
  min = slv.synthFun("min", [x, y], integer)

  # declare universal variables.
  varX = slv.declareSygusVar("x", integer)
  varY = slv.declareSygusVar("y", integer)

  max_x_y = slv.mkTerm(Kind.ApplyUf, max, varX, varY)
  min_x_y = slv.mkTerm(Kind.ApplyUf, min, varX, varY)

  # add semantic constraints
  # (constraint (>= (max x y) x))
  slv.addSygusConstraint(slv.mkTerm(Kind.Geq, max_x_y, varX))

  # (constraint (>= (max x y) y))
  slv.addSygusConstraint(slv.mkTerm(Kind.Geq, max_x_y, varY))

  # (constraint (or (= x (max x y))
  #                 (= y (max x y))))
  slv.addSygusConstraint(slv.mkTerm(
      Kind.Or, slv.mkTerm(Kind.Equal, max_x_y, varX), slv.mkTerm(Kind.Equal, max_x_y, varY)))

  # (constraint (= (+ (max x y) (min x y))
  #                (+ x y)))
  slv.addSygusConstraint(slv.mkTerm(
      Kind.Equal, slv.mkTerm(Kind.Add, max_x_y, min_x_y), slv.mkTerm(Kind.Add, varX, varY)))

  # print solutions if available
  if (slv.checkSynth().hasSolution()):
    # Output should be equivalent to:
    # (define-fun max ((x Int) (y Int)) Int (ite (<= x y) y x))
    # (define-fun min ((x Int) (y Int)) Int (ite (<= x y) x y))
    terms = [max, min]
    utils.print_synth_solutions(terms, slv.getSynthSolutions(terms))
