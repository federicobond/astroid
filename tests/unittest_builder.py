# Copyright (c) 2006-2014 LOGILAB S.A. (Paris, FRANCE) <contact@logilab.fr>
# Copyright (c) 2014-2020 Claudiu Popa <pcmanticore@gmail.com>
# Copyright (c) 2014-2015 Google, Inc.
# Copyright (c) 2015-2016 Ceridwen <ceridwenv@gmail.com>
# Copyright (c) 2015 Florian Bruhin <me@the-compiler.org>
# Copyright (c) 2016 Jakub Wilk <jwilk@jwilk.net>
# Copyright (c) 2017 Bryce Guinta <bryce.paul.guinta@gmail.com>
# Copyright (c) 2017 Łukasz Rogalski <rogalski.91@gmail.com>
# Copyright (c) 2018 Ville Skyttä <ville.skytta@iki.fi>
# Copyright (c) 2018 brendanator <brendan.maginnis@gmail.com>
# Copyright (c) 2018 Anthony Sottile <asottile@umich.edu>
# Copyright (c) 2019 Ashley Whetter <ashley@awhetter.co.uk>
# Copyright (c) 2019 Hugo van Kemenade <hugovk@users.noreply.github.com>
# Copyright (c) 2020-2021 hippo91 <guillaume.peillex@gmail.com>
# Copyright (c) 2021 Pierre Sassoulas <pierre.sassoulas@gmail.com>

# Licensed under the LGPL: https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html
# For details: https://github.com/PyCQA/astroid/blob/master/LICENSE

"""tests for the astroid builder and rebuilder module"""

import builtins
import collections
import os
import socket
import sys
import unittest

import pytest
from astroid import builder
from astroid import exceptions
from astroid import manager
from astroid import nodes
from astroid import test_utils
from astroid import util
from . import resources

MANAGER = manager.AstroidManager()
BUILTINS = builtins.__name__
PY38 = sys.version_info[:2] >= (3, 8)


class FromToLineNoTest(unittest.TestCase):
    def setUp(self):
        self.astroid = resources.build_file("data/format.py")

    def test_callfunc_lineno(self):
        stmts = self.astroid.body
        # on line 4:
        #    function('aeozrijz\
        #    earzer', hop)
        discard = stmts[0]
        self.assertIsInstance(discard, nodes.Expr)
        self.assertEqual(discard.fromlineno, 4)
        self.assertEqual(discard.tolineno, 5)
        callfunc = discard.value
        self.assertIsInstance(callfunc, nodes.Call)
        self.assertEqual(callfunc.fromlineno, 4)
        self.assertEqual(callfunc.tolineno, 5)
        name = callfunc.func
        self.assertIsInstance(name, nodes.Name)
        self.assertEqual(name.fromlineno, 4)
        self.assertEqual(name.tolineno, 4)
        strarg = callfunc.args[0]
        self.assertIsInstance(strarg, nodes.Const)
        if hasattr(sys, "pypy_version_info"):
            lineno = 4
        else:
            lineno = 5 if not PY38 else 4
        self.assertEqual(strarg.fromlineno, lineno)
        self.assertEqual(strarg.tolineno, lineno)
        namearg = callfunc.args[1]
        self.assertIsInstance(namearg, nodes.Name)
        self.assertEqual(namearg.fromlineno, 5)
        self.assertEqual(namearg.tolineno, 5)
        # on line 10:
        #    fonction(1,
        #             2,
        #             3,
        #             4)
        discard = stmts[2]
        self.assertIsInstance(discard, nodes.Expr)
        self.assertEqual(discard.fromlineno, 10)
        self.assertEqual(discard.tolineno, 13)
        callfunc = discard.value
        self.assertIsInstance(callfunc, nodes.Call)
        self.assertEqual(callfunc.fromlineno, 10)
        self.assertEqual(callfunc.tolineno, 13)
        name = callfunc.func
        self.assertIsInstance(name, nodes.Name)
        self.assertEqual(name.fromlineno, 10)
        self.assertEqual(name.tolineno, 10)
        for i, arg in enumerate(callfunc.args):
            self.assertIsInstance(arg, nodes.Const)
            self.assertEqual(arg.fromlineno, 10 + i)
            self.assertEqual(arg.tolineno, 10 + i)

    def test_function_lineno(self):
        stmts = self.astroid.body
        # on line 15:
        #    def definition(a,
        #                   b,
        #                   c):
        #        return a + b + c
        function = stmts[3]
        self.assertIsInstance(function, nodes.FunctionDef)
        self.assertEqual(function.fromlineno, 15)
        self.assertEqual(function.tolineno, 18)
        return_ = function.body[0]
        self.assertIsInstance(return_, nodes.Return)
        self.assertEqual(return_.fromlineno, 18)
        self.assertEqual(return_.tolineno, 18)
        self.skipTest(
            "FIXME  http://bugs.python.org/issue10445 "
            "(no line number on function args)"
        )

    def test_decorated_function_lineno(self):
        astroid = builder.parse(
            """
            @decorator
            def function(
                arg):
                print (arg)
            """,
            __name__,
        )
        function = astroid["function"]
        # XXX discussable, but that's what is expected by pylint right now
        self.assertEqual(function.fromlineno, 3)
        self.assertEqual(function.tolineno, 5)
        self.assertEqual(function.decorators.fromlineno, 2)
        self.assertEqual(function.decorators.tolineno, 2)

    def test_class_lineno(self):
        stmts = self.astroid.body
        # on line 20:
        #    class debile(dict,
        #                 object):
        #       pass
        class_ = stmts[4]
        self.assertIsInstance(class_, nodes.ClassDef)
        self.assertEqual(class_.fromlineno, 20)
        self.assertEqual(class_.tolineno, 22)
        self.assertEqual(class_.blockstart_tolineno, 21)
        pass_ = class_.body[0]
        self.assertIsInstance(pass_, nodes.Pass)
        self.assertEqual(pass_.fromlineno, 22)
        self.assertEqual(pass_.tolineno, 22)

    def test_if_lineno(self):
        stmts = self.astroid.body
        # on line 20:
        #    if aaaa: pass
        #    else:
        #        aaaa,bbbb = 1,2
        #        aaaa,bbbb = bbbb,aaaa
        if_ = stmts[5]
        self.assertIsInstance(if_, nodes.If)
        self.assertEqual(if_.fromlineno, 24)
        self.assertEqual(if_.tolineno, 27)
        self.assertEqual(if_.blockstart_tolineno, 24)
        self.assertEqual(if_.orelse[0].fromlineno, 26)
        self.assertEqual(if_.orelse[1].tolineno, 27)

    def test_for_while_lineno(self):
        for code in (
            """
            for a in range(4):
              print (a)
              break
            else:
              print ("bouh")
            """,
            """
            while a:
              print (a)
              break
            else:
              print ("bouh")
            """,
        ):
            astroid = builder.parse(code, __name__)
            stmt = astroid.body[0]
            self.assertEqual(stmt.fromlineno, 2)
            self.assertEqual(stmt.tolineno, 6)
            self.assertEqual(stmt.blockstart_tolineno, 2)
            self.assertEqual(stmt.orelse[0].fromlineno, 6)  # XXX
            self.assertEqual(stmt.orelse[0].tolineno, 6)

    def test_try_except_lineno(self):
        astroid = builder.parse(
            """
            try:
              print (a)
            except:
              pass
            else:
              print ("bouh")
            """,
            __name__,
        )
        try_ = astroid.body[0]
        self.assertEqual(try_.fromlineno, 2)
        self.assertEqual(try_.tolineno, 7)
        self.assertEqual(try_.blockstart_tolineno, 2)
        self.assertEqual(try_.orelse[0].fromlineno, 7)  # XXX
        self.assertEqual(try_.orelse[0].tolineno, 7)
        hdlr = try_.handlers[0]
        self.assertEqual(hdlr.fromlineno, 4)
        self.assertEqual(hdlr.tolineno, 5)
        self.assertEqual(hdlr.blockstart_tolineno, 4)

    def test_try_finally_lineno(self):
        astroid = builder.parse(
            """
            try:
              print (a)
            finally:
              print ("bouh")
            """,
            __name__,
        )
        try_ = astroid.body[0]
        self.assertEqual(try_.fromlineno, 2)
        self.assertEqual(try_.tolineno, 5)
        self.assertEqual(try_.blockstart_tolineno, 2)
        self.assertEqual(try_.finalbody[0].fromlineno, 5)  # XXX
        self.assertEqual(try_.finalbody[0].tolineno, 5)

    def test_try_finally_25_lineno(self):
        astroid = builder.parse(
            """
            try:
              print (a)
            except:
              pass
            finally:
              print ("bouh")
            """,
            __name__,
        )
        try_ = astroid.body[0]
        self.assertEqual(try_.fromlineno, 2)
        self.assertEqual(try_.tolineno, 7)
        self.assertEqual(try_.blockstart_tolineno, 2)
        self.assertEqual(try_.finalbody[0].fromlineno, 7)  # XXX
        self.assertEqual(try_.finalbody[0].tolineno, 7)

    def test_with_lineno(self):
        astroid = builder.parse(
            """
            from __future__ import with_statement
            with file("/tmp/pouet") as f:
                print (f)
            """,
            __name__,
        )
        with_ = astroid.body[1]
        self.assertEqual(with_.fromlineno, 3)
        self.assertEqual(with_.tolineno, 4)
        self.assertEqual(with_.blockstart_tolineno, 3)


class BuilderTest(unittest.TestCase):
    def setUp(self):
        self.builder = builder.AstroidBuilder()

    def test_data_build_null_bytes(self):
        with self.assertRaises(exceptions.AstroidSyntaxError):
            self.builder.string_build("\x00")

    def test_data_build_invalid_x_escape(self):
        with self.assertRaises(exceptions.AstroidSyntaxError):
            self.builder.string_build('"\\x1"')

    def test_missing_newline(self):
        """check that a file with no trailing new line is parseable"""
        resources.build_file("data/noendingnewline.py")

    def test_missing_file(self):
        with self.assertRaises(exceptions.AstroidBuildingError):
            resources.build_file("data/inexistant.py")

    def test_inspect_build0(self):
        """test astroid tree build from a living object"""
        builtin_ast = MANAGER.ast_from_module_name(BUILTINS)
        # just check type and object are there
        builtin_ast.getattr("type")
        objectastroid = builtin_ast.getattr("object")[0]
        self.assertIsInstance(objectastroid.getattr("__new__")[0], nodes.FunctionDef)
        # check open file alias
        builtin_ast.getattr("open")
        # check 'help' is there (defined dynamically by site.py)
        builtin_ast.getattr("help")
        # check property has __init__
        pclass = builtin_ast["property"]
        self.assertIn("__init__", pclass)
        self.assertIsInstance(builtin_ast["None"], nodes.Const)
        self.assertIsInstance(builtin_ast["True"], nodes.Const)
        self.assertIsInstance(builtin_ast["False"], nodes.Const)
        self.assertIsInstance(builtin_ast["Exception"], nodes.ClassDef)
        self.assertIsInstance(builtin_ast["NotImplementedError"], nodes.ClassDef)

    def test_inspect_build1(self):
        time_ast = MANAGER.ast_from_module_name("time")
        self.assertTrue(time_ast)
        self.assertEqual(time_ast["time"].args.defaults, [])

    def test_inspect_build3(self):
        self.builder.inspect_build(unittest)

    def test_inspect_build_type_object(self):
        builtin_ast = MANAGER.ast_from_module_name(BUILTINS)

        inferred = list(builtin_ast.igetattr("object"))
        self.assertEqual(len(inferred), 1)
        inferred = inferred[0]
        self.assertEqual(inferred.name, "object")
        inferred.as_string()  # no crash test

        inferred = list(builtin_ast.igetattr("type"))
        self.assertEqual(len(inferred), 1)
        inferred = inferred[0]
        self.assertEqual(inferred.name, "type")
        inferred.as_string()  # no crash test

    def test_inspect_transform_module(self):
        # ensure no cached version of the time module
        MANAGER._mod_file_cache.pop(("time", None), None)
        MANAGER.astroid_cache.pop("time", None)

        def transform_time(node):
            if node.name == "time":
                node.transformed = True

        MANAGER.register_transform(nodes.Module, transform_time)
        try:
            time_ast = MANAGER.ast_from_module_name("time")
            self.assertTrue(getattr(time_ast, "transformed", False))
        finally:
            MANAGER.unregister_transform(nodes.Module, transform_time)

    def test_package_name(self):
        """test base properties and method of an astroid module"""
        datap = resources.build_file("data/__init__.py", "data")
        self.assertEqual(datap.name, "data")
        self.assertEqual(datap.package, 1)
        datap = resources.build_file("data/__init__.py", "data.__init__")
        self.assertEqual(datap.name, "data")
        self.assertEqual(datap.package, 1)
        datap = resources.build_file("data/tmp__init__.py", "data.tmp__init__")
        self.assertEqual(datap.name, "data.tmp__init__")
        self.assertEqual(datap.package, 0)

    def test_yield_parent(self):
        """check if we added discard nodes as yield parent (w/ compiler)"""
        code = """
            def yiell(): #@
                yield 0
                if noe:
                    yield more
        """
        func = builder.extract_node(code)
        self.assertIsInstance(func, nodes.FunctionDef)
        stmt = func.body[0]
        self.assertIsInstance(stmt, nodes.Expr)
        self.assertIsInstance(stmt.value, nodes.Yield)
        self.assertIsInstance(func.body[1].body[0], nodes.Expr)
        self.assertIsInstance(func.body[1].body[0].value, nodes.Yield)

    def test_object(self):
        obj_ast = self.builder.inspect_build(object)
        self.assertIn("__setattr__", obj_ast)

    def test_newstyle_detection(self):
        data = """
            class A:
                "old style"

            class B(A):
                "old style"

            class C(object):
                "new style"

            class D(C):
                "new style"

            __metaclass__ = type

            class E(A):
                "old style"

            class F:
                "new style"
        """
        mod_ast = builder.parse(data, __name__)
        self.assertTrue(mod_ast["A"].newstyle)
        self.assertTrue(mod_ast["B"].newstyle)
        self.assertTrue(mod_ast["E"].newstyle)
        self.assertTrue(mod_ast["C"].newstyle)
        self.assertTrue(mod_ast["D"].newstyle)
        self.assertTrue(mod_ast["F"].newstyle)

    def test_globals(self):
        data = """
            CSTE = 1

            def update_global():
                global CSTE
                CSTE += 1

            def global_no_effect():
                global CSTE2
                print (CSTE)
        """
        astroid = builder.parse(data, __name__)
        self.assertEqual(len(astroid.getattr("CSTE")), 2)
        self.assertIsInstance(astroid.getattr("CSTE")[0], nodes.AssignName)
        self.assertEqual(astroid.getattr("CSTE")[0].fromlineno, 2)
        self.assertEqual(astroid.getattr("CSTE")[1].fromlineno, 6)
        with self.assertRaises(exceptions.AttributeInferenceError):
            astroid.getattr("CSTE2")
        with self.assertRaises(exceptions.InferenceError):
            next(astroid["global_no_effect"].ilookup("CSTE2"))

    def test_socket_build(self):
        astroid = self.builder.module_build(socket)
        # XXX just check the first one. Actually 3 objects are inferred (look at
        # the socket module) but the last one as those attributes dynamically
        # set and astroid is missing this.
        for fclass in astroid.igetattr("socket"):
            self.assertIn("connect", fclass)
            self.assertIn("send", fclass)
            self.assertIn("close", fclass)
            break

    def test_gen_expr_var_scope(self):
        data = "l = list(n for n in range(10))\n"
        astroid = builder.parse(data, __name__)
        # n unavailable outside gen expr scope
        self.assertNotIn("n", astroid)
        # test n is inferable anyway
        n = test_utils.get_name_node(astroid, "n")
        self.assertIsNot(n.scope(), astroid)
        self.assertEqual([i.__class__ for i in n.infer()], [util.Uninferable.__class__])

    def test_no_future_imports(self):
        mod = builder.parse("import sys")
        self.assertEqual(set(), mod.future_imports)

    def test_future_imports(self):
        mod = builder.parse("from __future__ import print_function")
        self.assertEqual({"print_function"}, mod.future_imports)

    def test_two_future_imports(self):
        mod = builder.parse(
            """
            from __future__ import print_function
            from __future__ import absolute_import
            """
        )
        self.assertEqual({"print_function", "absolute_import"}, mod.future_imports)

    def test_inferred_build(self):
        code = """
            class A: pass
            A.type = "class"

            def A_assign_type(self):
                print (self)
            A.assign_type = A_assign_type
            """
        astroid = builder.parse(code)
        lclass = list(astroid.igetattr("A"))
        self.assertEqual(len(lclass), 1)
        lclass = lclass[0]
        self.assertIn("assign_type", lclass.locals)
        self.assertIn("type", lclass.locals)

    def test_augassign_attr(self):
        builder.parse(
            """
            class Counter:
                v = 0
                def inc(self):
                    self.v += 1
            """,
            __name__,
        )
        # TODO: Check self.v += 1 generate AugAssign(AssAttr(...)),
        # not AugAssign(GetAttr(AssName...))

    def test_inferred_dont_pollute(self):
        code = """
            def func(a=None):
                a.custom_attr = 0
            def func2(a={}):
                a.custom_attr = 0
            """
        builder.parse(code)
        nonetype = nodes.const_factory(None)
        # pylint: disable=no-member; Infers two potential values
        self.assertNotIn("custom_attr", nonetype.locals)
        self.assertNotIn("custom_attr", nonetype.instance_attrs)
        nonetype = nodes.const_factory({})
        self.assertNotIn("custom_attr", nonetype.locals)
        self.assertNotIn("custom_attr", nonetype.instance_attrs)

    def test_asstuple(self):
        code = "a, b = range(2)"
        astroid = builder.parse(code)
        self.assertIn("b", astroid.locals)
        code = """
            def visit_if(self, node):
                node.test, body = node.tests[0]
            """
        astroid = builder.parse(code)
        self.assertIn("body", astroid["visit_if"].locals)

    def test_build_constants(self):
        """test expected values of constants after rebuilding"""
        code = """
            def func():
                return None
                return
                return 'None'
            """
        astroid = builder.parse(code)
        none, nothing, chain = [ret.value for ret in astroid.body[0].body]
        self.assertIsInstance(none, nodes.Const)
        self.assertIsNone(none.value)
        self.assertIsNone(nothing)
        self.assertIsInstance(chain, nodes.Const)
        self.assertEqual(chain.value, "None")

    def test_not_implemented(self):
        node = builder.extract_node(
            """
        NotImplemented #@
        """
        )
        inferred = next(node.infer())
        self.assertIsInstance(inferred, nodes.Const)
        self.assertEqual(inferred.value, NotImplemented)


class FileBuildTest(unittest.TestCase):
    def setUp(self):
        self.module = resources.build_file("data/module.py", "data.module")

    def test_module_base_props(self):
        """test base properties and method of an astroid module"""
        module = self.module
        self.assertEqual(module.name, "data.module")
        self.assertEqual(module.doc, "test module for astroid\n")
        self.assertEqual(module.fromlineno, 0)
        self.assertIsNone(module.parent)
        self.assertEqual(module.frame(), module)
        self.assertEqual(module.root(), module)
        self.assertEqual(module.file, os.path.abspath(resources.find("data/module.py")))
        self.assertEqual(module.pure_python, 1)
        self.assertEqual(module.package, 0)
        self.assertFalse(module.is_statement)
        self.assertEqual(module.statement(), module)
        self.assertEqual(module.statement(), module)

    def test_module_locals(self):
        """test the 'locals' dictionary of an astroid module"""
        module = self.module
        _locals = module.locals
        self.assertIs(_locals, module.globals)
        keys = sorted(_locals.keys())
        should = [
            "MY_DICT",
            "NameNode",
            "YO",
            "YOUPI",
            "__revision__",
            "global_access",
            "modutils",
            "four_args",
            "os",
            "redirect",
        ]
        should.sort()
        self.assertEqual(keys, sorted(should))

    def test_function_base_props(self):
        """test base properties and method of an astroid function"""
        module = self.module
        function = module["global_access"]
        self.assertEqual(function.name, "global_access")
        self.assertEqual(function.doc, "function test")
        self.assertEqual(function.fromlineno, 11)
        self.assertTrue(function.parent)
        self.assertEqual(function.frame(), function)
        self.assertEqual(function.parent.frame(), module)
        self.assertEqual(function.root(), module)
        self.assertEqual([n.name for n in function.args.args], ["key", "val"])
        self.assertEqual(function.type, "function")

    def test_function_locals(self):
        """test the 'locals' dictionary of an astroid function"""
        _locals = self.module["global_access"].locals
        self.assertEqual(len(_locals), 4)
        keys = sorted(_locals.keys())
        self.assertEqual(keys, ["i", "key", "local", "val"])

    def test_class_base_props(self):
        """test base properties and method of an astroid class"""
        module = self.module
        klass = module["YO"]
        self.assertEqual(klass.name, "YO")
        self.assertEqual(klass.doc, "hehe\n    haha")
        self.assertEqual(klass.fromlineno, 25)
        self.assertTrue(klass.parent)
        self.assertEqual(klass.frame(), klass)
        self.assertEqual(klass.parent.frame(), module)
        self.assertEqual(klass.root(), module)
        self.assertEqual(klass.basenames, [])
        self.assertTrue(klass.newstyle)

    def test_class_locals(self):
        """test the 'locals' dictionary of an astroid class"""
        module = self.module
        klass1 = module["YO"]
        locals1 = klass1.locals
        keys = sorted(locals1.keys())
        assert_keys = ["__init__", "__module__", "__qualname__", "a"]
        self.assertEqual(keys, assert_keys)
        klass2 = module["YOUPI"]
        locals2 = klass2.locals
        keys = locals2.keys()
        assert_keys = [
            "__init__",
            "__module__",
            "__qualname__",
            "class_attr",
            "class_method",
            "method",
            "static_method",
        ]
        self.assertEqual(sorted(keys), assert_keys)

    def test_class_instance_attrs(self):
        module = self.module
        klass1 = module["YO"]
        klass2 = module["YOUPI"]
        self.assertEqual(list(klass1.instance_attrs.keys()), ["yo"])
        self.assertEqual(list(klass2.instance_attrs.keys()), ["member"])

    def test_class_basenames(self):
        module = self.module
        klass1 = module["YO"]
        klass2 = module["YOUPI"]
        self.assertEqual(klass1.basenames, [])
        self.assertEqual(klass2.basenames, ["YO"])

    def test_method_base_props(self):
        """test base properties and method of an astroid method"""
        klass2 = self.module["YOUPI"]
        # "normal" method
        method = klass2["method"]
        self.assertEqual(method.name, "method")
        self.assertEqual([n.name for n in method.args.args], ["self"])
        self.assertEqual(method.doc, "method\n        test")
        self.assertEqual(method.fromlineno, 48)
        self.assertEqual(method.type, "method")
        # class method
        method = klass2["class_method"]
        self.assertEqual([n.name for n in method.args.args], ["cls"])
        self.assertEqual(method.type, "classmethod")
        # static method
        method = klass2["static_method"]
        self.assertEqual(method.args.args, [])
        self.assertEqual(method.type, "staticmethod")

    def test_method_locals(self):
        """test the 'locals' dictionary of an astroid method"""
        method = self.module["YOUPI"]["method"]
        _locals = method.locals
        keys = sorted(_locals)
        # ListComp variables are not accessible outside
        self.assertEqual(len(_locals), 3)
        self.assertEqual(keys, ["autre", "local", "self"])

    def test_unknown_encoding(self):
        with self.assertRaises(exceptions.AstroidSyntaxError):
            resources.build_file("data/invalid_encoding.py")


def test_module_build_dunder_file():
    """Test that module_build() can work with modules that have the *__file__* attribute"""
    module = builder.AstroidBuilder().module_build(collections)
    assert module.path[0] == collections.__file__


@pytest.mark.skipif(
    sys.version_info[:2] >= (3, 8),
    reason=(
        "The builtin ast module does not fail with a specific error "
        "for syntax error caused by invalid type comments."
    ),
)
def test_parse_module_with_invalid_type_comments_does_not_crash():
    node = builder.parse(
        """
    # op {
    #   name: "AssignAddVariableOp"
    #   input_arg {
    #     name: "resource"
    #     type: DT_RESOURCE
    #   }
    #   input_arg {
    #     name: "value"
    #     type_attr: "dtype"
    #   }
    #   attr {
    #     name: "dtype"
    #     type: "type"
    #   }
    #   is_stateful: true
    # }
    a, b = 2
    """
    )
    assert isinstance(node, nodes.Module)


if __name__ == "__main__":
    unittest.main()
