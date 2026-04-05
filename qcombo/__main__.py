#!/usr/bin/env python3
"""
qcombo - A package for computing commutators of many-body operators
         based on generalized Wick's theorem in quantum mechanics.

Usage examples:
    python -m qcombo 2 2
    python -m qcombo 2 2 --contraction 0,1,2
    python -m qcombo 2 2 --latex-output commutator.tex --amc-output commutator.amc
    python -m qcombo 2 2 -c 0,1 -lo commutator.tex -ao commutator.amc
"""

import sys
import argparse
from typing import List, Optional
import ast

# Import necessary functions from qcombo package
from . import easyCombo, __version__, __author__, __license__


def parse_contraction_argument(contraction_str: str) -> Optional[List[int]]:
    """
    Parse contraction argument, supporting multiple formats:
    - Single integer: "2"
    - Range: "0-3"
    - Comma separated: "0,1,2"
    - Mixed: "0,1-3,5"
    
    Args:
        contraction_str: Contraction argument string
        
    Returns:
        List of integers, or None (meaning calculate all possible contractions)
    """
    if contraction_str is None or contraction_str.lower() in ['none', 'all']:
        return None
    
    # If already a list, return directly
    if isinstance(contraction_str, list):
        return contraction_str
    
    # Try to parse as Python list
    try:
        if contraction_str.startswith('[') and contraction_str.endswith(']'):
            return ast.literal_eval(contraction_str)
    except:
        pass
    
    result = []
    parts = contraction_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Handle range
            range_parts = part.split('-')
            if len(range_parts) == 2:
                try:
                    start = int(range_parts[0].strip())
                    end = int(range_parts[1].strip())
                    result.extend(range(start, end + 1))
                except ValueError:
                    raise ValueError(f"Invalid range format: {part}")
            else:
                raise ValueError(f"Invalid range format: {part}")
        else:
            # Handle single number
            try:
                result.append(int(part))
            except ValueError:
                raise ValueError(f"Invalid number: {part}")
    
    # Remove duplicates and sort
    return sorted(set(result))


def cli_main():
    """Command line main function, unified entry point handler"""
    
    # Check if should enter interactive mode
    if len(sys.argv) == 1:
        # No arguments, enter interactive mode
        interactive_mode()
        return 0
    
    # Check if explicitly requesting interactive mode
    if len(sys.argv) == 2 and sys.argv[1] in ['-i', '--interactive']:
        interactive_mode()
        return 0
    
    # Check if requesting help or version
    if len(sys.argv) >= 2 and sys.argv[1] in ['-h', '--help', '-v', '--version']:
        # Let argparse handle these arguments
        pass
    
    parser = argparse.ArgumentParser(
        description="qcombo - Compute commutators of many-body operators (based on generalized Wick's theorem)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compute commutator of 2-body and 2-body operators, all possible contractions
  qcombo 2 2
  
  # Compute commutator of 2-body and 2-body operators, only 0-body and 1-body contractions
  qcombo 2 2 -c 0,1
  
  # Compute commutator of 1-body and 3-body operators, 0-2 body contractions
  qcombo 1 3 -c 0-2
  
  # Specify output filenames
  qcombo 2 2 -c 0,1,2 --latex-output my_commutator.tex --amc-output my_commutator.txt
  
  # Compute with specific indices (using Python list syntax)
  qcombo "[['a','b'], ['c','d']]" "[['e','f','g'], ['h','i','j']]" -c 0,1,2

Notes:
  - When left and right are integers, they represent the number of particles in the operators
  - When left and right are lists, they represent specific indices (using Python list syntax)
  - Contraction parameter can be: single integer(0), range(0-2), list(0,1,2), or 'all' (calculate all)
  - Run without arguments to enter interactive mode
        """
    )
    
    # Required arguments: left and right
    parser.add_argument(
        "left",
        help="Number of particles in left operator (integer) or index list (Python list string)"
    )
    
    parser.add_argument(
        "right",
        help="Number of particles in right operator (integer) or index list (Python list string)"
    )
    
    # Optional arguments
    parser.add_argument(
        "-c", "--contraction",
        help="Contraction body numbers: single integer(0), range(0-2), list(0,1,2), or 'all' (calculate all). Default: all"
    )
    
    parser.add_argument(
        "--latex-output", '-lo',
        help="LaTeX output filename. Default: auto-generated based on operators"
    )
    
    parser.add_argument(
        "--amc-output", '-ao',
        help="AMC program input file output name. Default: auto-generated based on operators"
    )

    parser.add_argument(
        "--left-indices",
        help="Custom indices for left operator when LEFT is integer, format: \"[['i','j'],['a','b']]\""
    )

    parser.add_argument(
        "--right-indices",
        help="Custom indices for right operator when RIGHT is integer, format: \"[['k','l'],['c','d']]\""
    )

    parser.add_argument(
        "--intermediate-indices",
        help="Custom intermediate (summation) index names, format: \"['p','q','r']\""
    )

    parser.add_argument(
        "--intermediate-prefix",
        default="x",
        help="Prefix for auto-generated intermediate indices (default: x, producing x0,x1,...)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"qcombo v{__version__} by {__author__} (License: {__license__})"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode, reduce output"
    )
    
    # Add interactive mode parameter
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive mode"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if should enter interactive mode
    if args.interactive:
        interactive_mode()
        return 0
    
    # Parse left and right arguments
    try:
        # Try to parse as integer
        left = int(args.left)
    except ValueError:
        # If not integer, try to parse as Python list
        try:
            left = ast.literal_eval(args.left)
            if not isinstance(left, list):
                raise ValueError("Left argument must be integer or list")
        except:
            parser.error(f"Cannot parse left argument: {args.left}")
    
    try:
        # Try to parse as integer
        right = int(args.right)
    except ValueError:
        # If not integer, try to parse as Python list
        try:
            right = ast.literal_eval(args.right)
            if not isinstance(right, list):
                raise ValueError("Right argument must be integer or list")
        except:
            parser.error(f"Cannot parse right argument: {args.right}")
    
    # Validate left and right arguments
    if isinstance(left, int) and left <= 0:
        parser.error("Left argument must be a positive integer")
    if isinstance(right, int) and right <= 0:
        parser.error("Right argument must be a positive integer")
    
    if isinstance(left, list) and isinstance(right, list):
        # Check list structure
        if len(left) != 2 or len(right) != 2:
            parser.error("Index lists must be 2D lists, e.g.: [['a','b'], ['c','d']]")
    
    # Parse contraction argument
    try:
        contraction = parse_contraction_argument(args.contraction)
    except ValueError as e:
        parser.error(f"Invalid contraction argument: {e}")

    # Parse custom index options
    try:
        left_indices = ast.literal_eval(args.left_indices) if args.left_indices else None
        right_indices = ast.literal_eval(args.right_indices) if args.right_indices else None
        intermediate_indices = ast.literal_eval(args.intermediate_indices) if args.intermediate_indices else None
    except Exception as e:
        parser.error(f"Invalid custom index format: {e}")
    
    # Print start information
    if not args.quiet:
        print(f"qcombo v{__version__}")
        print(f"Computing commutator: {left} with {right}")
        if contraction is None:
            print("Calculating all possible contractions")
        else:
            print(f"Calculating contraction body numbers: {contraction}")
        print("-" * 50)
    
    try:
        # Call easyCombo function
        result = easyCombo(
            left=left,
            right=right,
            contraction=contraction,
            latexOutput=args.latex_output,
            amcOutput=args.amc_output,
            left_indices=left_indices,
            right_indices=right_indices,
            intermediate_indices=intermediate_indices,
            intermediate_prefix=args.intermediate_prefix
        )
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1


# Interactive mode helper function
def interactive_mode():
    """Interactive mode for exploratory calculations"""
    print("=" * 60)
    print("qcombo Interactive Mode")
    print("Enter 'quit' or 'q' to exit")
    print("=" * 60)
    
    while True:
        try:
            # Get left operator
            left_input = input("\nLeft operator (integer or list, e.g.: 2 or [['a','b'], ['c','d']]): ").strip()
            if left_input.lower() in ['quit', 'q', 'exit']:
                break
            
            # Get right operator
            right_input = input("Right operator (integer or list): ").strip()
            if right_input.lower() in ['quit', 'q', 'exit']:
                break
            
            # Get contraction parameter
            contraction_input = input("Contraction body numbers (integer, range or list, press Enter for 'all'): ").strip()
            if contraction_input.lower() in ['quit', 'q', 'exit']:
                break
            
            if contraction_input == '':
                contraction_input = 'all'
            
            # Parse arguments
            try:
                left = int(left_input) if left_input.isdigit() else ast.literal_eval(left_input)
                right = int(right_input) if right_input.isdigit() else ast.literal_eval(right_input)
                contraction = parse_contraction_argument(contraction_input)
            except Exception as e:
                print(f"Argument parsing error: {e}")
                continue
            
            
            latex_file = input("LaTeX filename (press Enter for default): ").strip()
            if latex_file == '':
                latex_file = None
            
            amc_file = input("AMC filename (press Enter for default): ").strip()
            if amc_file == '':
                amc_file = None

            intermediate_input = input("Intermediate index names (list, optional, e.g. ['p','q']): ").strip()
            if intermediate_input == '':
                intermediate_indices = None
            else:
                intermediate_indices = ast.literal_eval(intermediate_input)

            intermediate_prefix = input("Intermediate index prefix (default x): ").strip()
            if intermediate_prefix == '':
                intermediate_prefix = 'x'

            # Execute calculation
            print(f"\nComputing commutator: {left} with {right}")
            if contraction is None:
                print("Calculating all possible contractions")
            else:
                print(f"Calculating contraction body numbers: {contraction}")
            print("-" * 50)
            
            # Calculate and save
            result = easyCombo(
                left=left,
                right=right,
                contraction=contraction,
                latexOutput=latex_file,
                amcOutput=amc_file,
                intermediate_indices=intermediate_indices,
                intermediate_prefix=intermediate_prefix
            )
                
            
        except KeyboardInterrupt:
            print("\n\nInterrupted, exiting interactive mode")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main function for backward compatibility"""
    return cli_main()


if __name__ == "__main__":
    # When called via python -m qcombo, use cli_main
    sys.exit(cli_main())
