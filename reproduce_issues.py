#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
from kfta_parser import KFTAParser

def main():
    print("🔍 KFTA Excel Logic Verification")
    parser = KFTAParser()
    
    # 1. Test On-ui Kindergarten (온의유치원)
    print("\n[Test 1] On-ui Kindergarten Mapping")
    school = "온의유치원"
    edu_office = parser.find_education_office_for_school(school)
    print(f"Input: {school}")
    print(f"Output: {edu_office}")
    if "춘천" in edu_office:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        
    # 2. Test School Name Region Prefix Removal logic
    print("\n[Test 2] Region Prefix Removal")
    test_cases = [
        ("춘천초등학교", "춘천초등학교"), # Should NOT remove
        ("춘천 초등학교", "초등학교"),     # Should remove
        ("철원 새들유치원", "새들유치원"), # Should remove
        ("강릉여자고등학교", "강릉여자고등학교"), # Should NOT remove
    ]
    
    for input_name, expected in test_cases:
        result = parser.remove_region_prefix_from_school_name(input_name)
        print(f"Input: '{input_name}' -> Output: '{result}' | Expected: '{expected}'")
        if result == expected:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            
    # 3. Test Special Schools
    print("\n[Test 3] Special Schools Mapping")
    special_schools = ["춘천동원학교", "춘천계성학교"]
    for school in special_schools:
        edu_office = parser.find_education_office_for_school(school)
        print(f"Input: {school}")
        print(f"Output: {edu_office}")
        if "춘천" in edu_office:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            
    # 4. Test Other Provinces (Fix 4)
    print("\n[Test 4] Other Provinces")
    other_regions = ["서울", "경기", "광주"]
    for region in other_regions:
        edu_office = parser.get_education_office(region)
        print(f"Input: {region}")
        print(f"Output: '{edu_office}'")
        if edu_office == "":
            print("✅ PASS")
        else:
            print("❌ FAIL")

    # 5. Test Remarks Parsing (Fix 5 & 9)
    print("\n[Test 5] Remarks Parsing")
    
    # Mock Row structure (indices based on kfta_parser.py)
    # 0, 1, 2(Name), 3, 4(Pos), 5(NewSchool), 6, 7(CurrentSchool/Region), 8(Subject), 9(Remarks)
    
    # Case A: Remarks has School Name "전입(서울 OO초)"
    row_a = pd.Series(["", "", "홍길동", "", "교사", "춘천초등학교", "", "", "", "전입(서울 OO초)"])
    result_a = parser.parse_row_to_kfta(row_a)
    print(f"Case A (Previous School in Remarks): {result_a['현재분회']}")
    if "OO초등학교" in result_a['현재분회'] or "OO초" in result_a['현재분회']: # Exact expanding depends on implementation
         print("✅ PASS")
    else:
         print(f"❌ FAIL - Got: {result_a['현재분회']}")
         
    # Case B: Remarks has "춘천동원학교"
    row_b = pd.Series(["", "", "손경자", "", "특수교사", "강원특별자치도교육청", "", "", "", "춘천동원학교"])
    result_b = parser.parse_row_to_kfta(row_b)
    print(f"Case B (School in Remarks): {result_b['현재분회']}, {result_b['현재교육청']}")
    if "동원학교" in result_b['현재분회'] and "춘천" in result_b['현재교육청']:
        print("✅ PASS")
    else:
        print("❌ FAIL")

    # Case C: Remarks has "타시도전입(경기)"
    row_c = pd.Series(["", "", "이몽룡", "", "교사", "원주중학교", "", "", "", "타시도전입(경기)"])
    result_c = parser.parse_row_to_kfta(row_c)
    print(f"Case C (Other Province in Remarks): Current Edu Office='{result_c['현재교육청']}'")
    if result_c['현재교육청'] == "":
        print("✅ PASS")
    else:
        print("❌ FAIL")

if __name__ == "__main__":
    main()
