#!/bin/bash

echo "==============================="
echo "CLASS DEFINITIONS"
echo "==============================="

grep -R "^class " -n .

echo ""
echo "==============================="
echo "GENERATE METHODS"
echo "==============================="

grep -R "def generate" -n .

echo ""
echo "==============================="
echo "RUN METHODS"
echo "==============================="

grep -R "def run" -n .

echo ""
echo "==============================="
echo "ENGINE IMPORTS"
echo "==============================="

grep -R "Engine" -n pipeline/
