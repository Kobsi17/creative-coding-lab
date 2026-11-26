import ast
import asyncio
import os
import sys
import time

from pathlib import Path


def matches(node, expression):
    return ast.dump(node) == ast.dump(ast.parse(expression, mode="eval").body)


class BrowserLoop(ast.NodeTransformer):
    def visit_While(self, node):
        self.generic_visit(node)
        node.body.insert(0, ast.parse("await _lab_asyncio.sleep(0)", mode="exec").body[0])
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if matches(node.func, "clock.tick") and len(node.args) == 1 and not node.keywords:
            return ast.Await(ast.Call(
                ast.Name("_lab_tick", ast.Load()),
                [ast.Name("clock", ast.Load()), *node.args],
                [],
            ))
        return node

    def visit_FunctionDef(self, node):
        return node

    def visit_AsyncFunctionDef(self, node):
        return node

    def visit_ClassDef(self, node):
        return node


def compile_sketch(source, filename):
    tree = ast.parse(source, filename=filename)
    main = next((node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "main"), None)
    if main is not None:
        for guard in tree.body:
            if not isinstance(guard, ast.If) or not matches(guard.test, '__name__ == "__main__"'):
                continue
            for statement in guard.body:
                if not isinstance(statement, ast.Expr):
                    continue
                if matches(statement.value, "main()") or matches(statement.value, "sys.exit(main())"):
                    fields = {field: getattr(main, field) for field in main._fields}
                    replacement = ast.AsyncFunctionDef(**fields)
                    replacement.body = [BrowserLoop().visit(node) for node in main.body]
                    tree.body[tree.body.index(main)] = ast.copy_location(replacement, main)
                    statement.value = ast.Await(ast.parse("main()", mode="eval").body)
                    return compile(ast.fix_missing_locations(tree), filename, "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    tree = BrowserLoop().visit(tree)
    return compile(ast.fix_missing_locations(tree), filename, "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)


async def run_sketch(source, filename):
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    path = Path("/home/pyodide") / Path(filename).name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)
    sys.argv = [str(path)]
    last_tick = {}

    async def tick(clock, fps):
        now = time.monotonic()
        if fps > 0:
            await asyncio.sleep(max(0, 1 / fps - (now - last_tick.get(clock, now))))
        last_tick[clock] = time.monotonic()
        return clock.tick()

    namespace = {
        "__name__": "__main__",
        "__file__": str(path),
        "_lab_asyncio": asyncio,
        "_lab_tick": tick,
    }
    task = eval(compile_sketch(source, str(path)), namespace)
    if task is not None:
        await task
