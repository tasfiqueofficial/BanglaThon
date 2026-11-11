"""
Comprehensive Test Suite for Bangla Programming Language
==========================================================
সমস্ত ভাষার বৈশিষ্ট্য পরীক্ষা করার জন্য পরীক্ষা কেস।

Run: python3 test_bangla.py
"""

from lexer import Lexer, LexerError
from parser import Parser, ParserError
from interpreter import Interpreter, BanglaRuntimeError
import sys


def run_test(name, code, expected_output=None, should_fail=False):
    """একটি Bangla code স্নিপেট পরীক্ষা করুন।"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print("Code:")
    print(code)
    print()

    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        
        # Capture output
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            interpreter.interpret(ast)
        
        output = f.getvalue()
        
        if should_fail:
            print(f"❌ FAILED: Expected an error but succeeded")
            print(f"Output: {output}")
            return False
        
        print("Output:")
        print(output if output else "(no output)")
        
        if expected_output is not None and output.strip() != expected_output.strip():
            print(f"❌ FAILED: Output mismatch")
            print(f"Expected:\n{expected_output}")
            return False
        
        print("✅ PASSED")
        return True
        
    except (LexerError, ParserError, BanglaRuntimeError) as e:
        if should_fail:
            print(f"✅ PASSED (error as expected): {e}")
            return True
        print(f"❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False


def main():
    results = []
    
    # Test 1: Basic variable declaration
    results.append(run_test(
        "Basic Variable Declaration",
        '''dhori x = 10
dhori y = 20
dekhao x
dekhao y
''',
        expected_output="10\n20"
    ))
    
    # Test 2: Arithmetic operations
    results.append(run_test(
        "Arithmetic Operations",
        '''dhori a = 5
dhori b = 3
dekhao a + b
dekhao a - b
dekhao a * b
dekhao a / b
dekhao a % b
''',
        expected_output="8\n2\n15\n1.6666666666666667\n2"
    ))
    
    # Test 3: String operations
    results.append(run_test(
        "String Operations",
        '''dhori naam = "Bangla"
dhori greeting = "Hello"
dekhao greeting
dekhao naam
''',
        expected_output="Hello\nBangla"
    ))
    
    # Test 4: String concatenation
    results.append(run_test(
        "String Concatenation",
        '''dhori greeting = "Hello " + "World"
dekhao greeting
''',
        expected_output="Hello World"
    ))
    
    # Test 5: Boolean operations
    results.append(run_test(
        "Boolean Operations",
        '''dhori shotti_val = shotti
dhori mittha_val = mittha
dekhao shotti_val
dekhao mittha_val
''',
        expected_output="shotti\nmittha"
    ))
    
    # Test 6: If-else statement
    results.append(run_test(
        "If-Else Statement",
        '''dhori x = 15
jodi (x > 10) {
    dekhao "boro"
} nahole {
    dekhao "choto"
}
''',
        expected_output="boro"
    ))
    
    # Test 7: Else-if chain
    results.append(run_test(
        "Else-If Chain",
        '''dhori x = 10
jodi (x > 15) {
    dekhao "prosno"
} nahole jodi (x == 10) {
    dekhao "samman"
} nahole {
    dekhao "choto"
}
''',
        expected_output="samman"
    ))
    
    # Test 8: While loop
    results.append(run_test(
        "While Loop",
        '''dhori i = 0
jotokkhon (i < 3) {
    dekhao i
    i = i + 1
}
''',
        expected_output="0\n1\n2"
    ))
    
    # Test 9: For loop
    results.append(run_test(
        "For Loop",
        '''jonno (dhori i = 0; i < 3; i = i + 1) {
    dekhao i
}
''',
        expected_output="0\n1\n2"
    ))
    
    # Test 10: Break statement
    results.append(run_test(
        "Break Statement",
        '''jonno (dhori i = 0; i < 5; i = i + 1) {
    jodi (i == 3) {
        thamo
    }
    dekhao i
}
''',
        expected_output="0\n1\n2"
    ))
    
    # Test 11: Continue statement
    results.append(run_test(
        "Continue Statement",
        '''jonno (dhori i = 0; i < 5; i = i + 1) {
    jodi (i == 2) {
        cholo
    }
    dekhao i
}
''',
        expected_output="0\n1\n3\n4"
    ))
    
    # Test 12: Function definition and call
    results.append(run_test(
        "Function Definition and Call",
        '''kaj jog(a, b) {
    ferot a + b
}
dhori result = jog(2, 3)
dekhao result
''',
        expected_output="5"
    ))
    
    # Test 13: Function with no return
    results.append(run_test(
        "Function with No Return",
        '''kaj greet(naam) {
    dekhao "Hello " + naam
}
greet("Bangla")
''',
        expected_output="Hello Bangla"
    ))
    
    # Test 14: Array/List operations
    results.append(run_test(
        "Array/List Operations",
        '''dhori nums = talika(1, 2, 3, 4, 5)
dekhao nums
dekhao nums[0]
dekhao nums[2]
''',
        expected_output="[1, 2, 3, 4, 5]\n1\n3"
    ))
    
    # Test 15: List mutation
    results.append(run_test(
        "List Mutation",
        '''dhori nums = talika(1, 2, 3)
nums[1] = 99
dekhao nums
''',
        expected_output="[1, 99, 3]"
    ))
    
    # Test 16: Built-in: dhoirgo (length)
    results.append(run_test(
        "Built-in dhoirgo (length)",
        '''dhori nums = talika(1, 2, 3, 4, 5)
dekhao dhoirgo(nums)
dhori s = "Bangla"
dekhao dhoirgo(s)
''',
        expected_output="5\n6"
    ))
    
    # Test 17: Built-in: juktokoro (append)
    results.append(run_test(
        "Built-in juktokoro (append)",
        '''dhori nums = talika(1, 2, 3)
juktokoro(nums, 4)
juktokoro(nums, 5)
dekhao nums
''',
        expected_output="[1, 2, 3, 4, 5]"
    ))
    
    # Test 18: Built-in: shajao (sort)
    results.append(run_test(
        "Built-in shajao (sort)",
        '''dhori nums = talika(3, 1, 4, 1, 5)
dhori sorted_nums = shajao(nums)
dekhao sorted_nums
''',
        expected_output="[1, 1, 3, 4, 5]"
    ))
    
    # Test 19: Built-in: ulto (reverse)
    results.append(run_test(
        "Built-in ulto (reverse)",
        '''dhori nums = talika(1, 2, 3, 4, 5)
dekhao ulto(nums)
dhori s = "Bangla"
dekhao ulto(s)
''',
        expected_output="[5, 4, 3, 2, 1]\nalgnaB"
    ))
    
    # Test 20: Built-in: jog_koro (sum)
    results.append(run_test(
        "Built-in jog_koro (sum)",
        '''dhori nums = talika(1, 2, 3, 4, 5)
dekhao jog_koro(nums)
''',
        expected_output="15"
    ))
    
    # Test 21: Built-in: shorbo_boro (max)
    results.append(run_test(
        "Built-in shorbo_boro (max)",
        '''dhori nums = talika(3, 1, 4, 1, 5, 9)
dekhao shorbo_boro(nums)
''',
        expected_output="9"
    ))
    
    # Test 22: Built-in: shorbo_choto (min)
    results.append(run_test(
        "Built-in shorbo_choto (min)",
        '''dhori nums = talika(3, 1, 4, 1, 5, 9)
dekhao shorbo_choto(nums)
''',
        expected_output="1"
    ))
    
    # Test 23: Logical operators (ebong/ba/noy)
    results.append(run_test(
        "Logical Operators",
        '''dekhao shotti ebong shotti
dekhao shotti ebong mittha
dekhao shotti ba mittha
dekhao mittha ba mittha
dekhao noy shotti
dekhao noy mittha
''',
        expected_output="shotti\nmittha\nshotti\nmittha\nmittha\nshotti"
    ))
    
    # Test 24: Comparison operators
    results.append(run_test(
        "Comparison Operators",
        '''dekhao 5 > 3
dekhao 5 < 3
dekhao 5 >= 5
dekhao 5 <= 5
dekhao 5 == 5
dekhao 5 != 3
''',
        expected_output="shotti\nmittha\nshotti\nshotti\nshotti\nshotti"
    ))
    
    # Test 25: Unary minus
    results.append(run_test(
        "Unary Minus",
        '''dhori x = 10
dekhao -x
dekhao -(-5)
''',
        expected_output="-10\n5"
    ))
    
    # Test 26: Complex expression
    results.append(run_test(
        "Complex Expression",
        '''dekhao 2 + 3 * 4
dekhao (2 + 3) * 4
''',
        expected_output="14\n20"
    ))
    
    # Test 27: Nested function calls
    results.append(run_test(
        "Nested Function Calls",
        '''kaj double(x) {
    ferot x * 2
}
kaj add(a, b) {
    ferot a + b
}
dekhao double(add(2, 3))
''',
        expected_output="10"
    ))
    
    # Test 28: Scope and closure
    results.append(run_test(
        "Scope Test",
        '''dhori global_var = 100
kaj test() {
    dhori local_var = 50
    dekhao global_var
    dekhao local_var
}
test()
''',
        expected_output="100\n50"
    ))
    
    # Test 29: Error handling - undefined variable
    results.append(run_test(
        "Error: Undefined Variable",
        '''dekhao undefined_var
''',
        should_fail=True
    ))
    
    # Test 30: Error handling - division by zero
    results.append(run_test(
        "Error: Division by Zero",
        '''dekhao 10 / 0
''',
        should_fail=True
    ))

    # Test 31: Native Bangla print (user request example)
    results.append(run_test(
        "Native Bangla Print",
        '''দেখাও "তুমি কেমন আছো"
''',
        expected_output="তুমি কেমন আছো"
    ))

    # Test 32: Native Bangla variables, digits, quotes, and Dari (।)
    results.append(run_test(
        "Native Bangla Variables & Numerals",
        '\ufeff' + '''ধরি নাম = 'বাংলাদেশ'।
ধরি সাল = ২০২৬।
ধরি দশমিক_মান = ৩.৫
দেখাও নাম + " " + সাল + " " + দশমিক_মান
দেখাও “ভালো থেকো”
''',
        expected_output="বাংলাদেশ 2026 3.5\nভালো থেকো"
    ))

    # Test 33: Mixed Banglish and Native Bangla in same script
    results.append(run_test(
        "Mixed Banglish + Native Bangla Syntax",
        '''ধরি x = ১০
dhori y = 20
যদি (x < y এবং সত্যি) {
    dekhao x + y
} নাহলে {
    দেখাও "সমান বা বড়"
}
''',
        expected_output="30"
    ))

    # Test 34: Native Bangla loops (যতক্ষণ, জন্য, থামো, চলো) & compound assignments
    results.append(run_test(
        "Native Bangla Loops & Compound Assignment",
        '''ধরি মোট = ০
জন্য (ধরি ক = ১; ক <= ১০; ক += ১) {
    যদি (ক == ৩) { চলো }
    যদি (ক == ৬) { থামো }
    মোট += ক
}
দেখাও মোট

ধরি সংখ্যা = ৪
যতক্ষণ (সংখ্যা > ০) {
    সংখ্যা -= ২
}
দেখাও সংখ্যা
''',
        expected_output="12\n0"
    ))

    # Test 35: Native Bangla functions, recursion, and boolean/logic (নয় vs নয় NFC)
    results.append(run_test(
        "Native Bangla Functions & Logic",
        '''কাজ গুনফল(ক, খ) {
    ফেরত ক * খ
}
দেখাও গুনফল(৬, ৭)
দেখাও সত্য এবং মিথ্যা
দেখাও সত্য অথবা মিথ্যা
দেখাও নয় মিথ্যা
দেখাও নয় সত্যি
''',
        expected_output="42\nmittha\nshotti\nshotti\nmittha"
    ))

    # Test 36: Native Bangla lists, [] literals, and list built-ins
    results.append(run_test(
        "Native Bangla List Built-ins & Bracket Literals",
        '''ধরি তালিকা_১ = তালিকা(৫, ২, ৮, ১)
ধরি তালিকা_২ = [১০, ২০, ৩০]
যুক্তকরো(তালিকা_১, ৯)
দেখাও সাজাও(তালিকা_১)
দেখাও উল্টো(তালিকা_১)
দেখাও যোগ_করো(তালিকা_১)
দেখাও সর্বোচ্চ(তালিকা_১)
দেখাও সর্বনিম্ন(তালিকা_১)
দেখাও দৈর্ঘ্য(তালিকা_২)
দেখাও বাদ_দাও(তালিকা_২, ১)
দেখাও তালিকা_২
দেখাও আছে(তালিকা_২, ৩০)
দেখাও পরিসর(১, ৬, ২)
''',
        expected_output="[1, 2, 5, 8, 9]\n[9, 1, 8, 2, 5]\n25\n9\n1\n3\n20\n[10, 30]\nshotti\n[1, 3, 5]"
    ))

    # Test 37: New Math, Power (**), Type Conversion & String Built-ins
    results.append(run_test(
        "Math, Type Conversion & String Built-ins",
        '''দেখাও ২ ** ৩ ** ২
দেখাও -২ ** ২
দেখাও ২ ** -১
দেখাও ঘাত(৩, ৪)
দেখাও বর্গমূল(৮১)
দেখাও পরম(-২৫)
দেখাও পূর্ণ("৪২") + ৮
দেখাও দশমিক("৩.৫") * ২
দেখাও ধরন(১২৩)
দেখাও ধরন("হ্যালো")
দেখাও ধরন(সত্যি)
দেখাও ধরন(খালি)
দেখাও ধরন([১, ২])
দেখাও বড়_হাতের("bangla")
দেখাও ছোট_হাতের("BANGLA")
দেখাও ভাঙো("আমি বাংলায় কোড লিখি")
''',
        expected_output="512\n-4\n0.5\n81\n9\n25\n50\n7.0\nshongkha\nlekha\nshotti_mittha\nkhali\ntalika\nBANGLA\nbangla\n[আমি, বাংলায়, কোড, লিখি]"
    ))

    # Test 38: Error handling - negative square root
    results.append(run_test(
        "Error: Negative sqrt",
        '''দেখাও বর্গমূল(-9)
''',
        should_fail=True
    ))

    # Test 39: Error handling - modulo by zero
    results.append(run_test(
        "Error: Modulo by Zero",
        '''দেখাও ১০ % ০
''',
        should_fail=True
    ))

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
