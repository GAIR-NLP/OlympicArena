# Environment Setup

Please ensure you have installed the following package in your environment:

```bash
pip install streamlit==1.32.1
```

**It is recommended to use Firefox browser to avoid compatibility issues**, especially when rendering large PDF files. You can download and install Firefox browser from the following link: [Mozilla Firefox Official Website](https://www.firefox.com.cn/). Edge and Chrome browsers encounter issues when rendering large PDF files.

# Prepare Files for Annotation

Before starting, please create a folder named `data` in the current working directory and organize your files as follows: (The specific data files are in the project's Google Drive)

```
data
├── Math
│ ├── JHMT
│ └── ...
├── Chemistry
└── ...
```

This will ensure that the program can correctly locate and organize your files.

# Launch the Application

Once setup is complete, run the following command in the terminal to start the application:

```bash
streamlit run main.py
```

Follow the instructions to open the application in your web browser. If everything is set up correctly, you should be able to see the main interface of the application.

# User Guide

## Steps to Use
### 1. Select File
Select (subject, competition, file), and the interface will automatically display the PDF and markdown preview of the file.

**All annotated outputs are stored as ./subject/competition_abbreviation/file_name/date_marker.json in the ./output/ folder. (One JSON per problem)**

### 2. Select problem Type
The system supports the following types of problems:
| Abbreviation | Answer Type           | Description                                                                          |
|--------------|-----------------------|--------------------------------------------------------------------------------------|
| SC           | Single Choice         | Multiple choice problems with only one correct option (e.g., four options, five options) |
| MC           | Multiple Choice       | Multiple choice problems with more than one correct option (e.g., two out of four, two out of five) |
| TF           | True/False            | True/False problems                                                                 |
| NV           | Numerical Value       | Answer is a numerical value, special values like $\pi$, $e$, $\sqrt{7}$, $log_29$ are represented using tex |
| SET          | Set                   | Answer is a set, such as {1, 2, 3}                                                   |
| IN           | Interval              | Answer is a range of values, written in interval notation using tex                  |
| EX           | Expression            | Answer is an expression containing letters, represented in tex format                |
| EQ           | Equation              | Answer is an equation containing letters, represented in tex format                  |
| TUP          | Tuple                 | Usually represents a pair of values, such as (x, y)                                  |
| MPV          | Multiple Values       | One problem with multiple values to find, e.g., the first sub-problem of a physics problem requires both speed and time |
| MA           | Multiple Answers      | One problem with multiple correct answers, e.g., a math fill-in-the-blank problem with answers 1 or -2 |
| OT           | Other (Human Evaluation Required) | problems not easily evaluated automatically, such as writing chemical equations, explaining reasons, etc., require model evaluation |

**Note: In the modes of multiple values per problem and multiple answers per problem, each value can be a numerical value, interval, expression, equation, set, or tuple (this option is available in the annotation interface).**


### 3. Annotation
- Context: Some problems require conclusions or information from previous sub-problems to better solve the next sub-problem. For example, in a physics problem with three sub-problems, the third sub-problem may rely on the conclusions from the first two sub-problems. Therefore, the context section needs you to summarize and supplement some previously derived conclusions and information (for example, you can copy the solutions or answers from the previous sub-problems).

- problem Stem: The problem description. After completing the annotation, you can preview to check if it conforms to the tex syntax format. If you find any errors, you can use the original PDF to re-parse and correct it using [mathpix](https://mathpix.com/) (paid) or [latexlive](https://www.latexlive.com/) (free).
- Answer: Annotate according to the requirements of different problem types ([see details](#annotation-requirements-for-different-problem-types)).
- Solution: If the file provides not only the standard answer but also a detailed solution, you need to annotate this section (do not include irrelevant characters or symbols, such as [Solution]).
- Images: If any part of a problem's **stem/options (if multiple choice)/solution** contains an image, you need to annotate this field.

Annotation Method:
**In the problem stem/options (if multiple choice)/solution, represent images in the form of a URL link**.
For example:

https://cdn.mathpix.com/cropped/2024_03_14_b9e515217a571029676eg-10.jpg?height=488&width=808&top_left_y=1389&top_left_x=1092

#### Annotation Requirements for Different problem Types
- Single Choice, Multiple Choice, True/False

  Simply add the options one by one and select the correct option.
- Numerical Value

  Simple values can be filled in directly with numbers. Complex values or those with special symbols should be represented using tex, such as `$e^{i \pi}+1$` to represent $e^{i \pi}+1$.

  If the numerical value has a unit, such as m/s in physics or mol/L in chemistry, fill in the unit field. If there is no unit, leave it blank.
- Set

  Enclose the set in `{}`. For example, `{1, 2, $e$, $log _2 3$}` represents {1, 2, $e$, $log _2 3$}.

- Interval, Expression, Equation

  Similar to numerical values, they are all represented using tex.

- Tuple

  Usually a pair of values (occasionally seen in mathematics). For example, to find the pair $(x, y)$ that satisfies the conditions, the answer is $(2, 3)$.

- Multiple Values per problem

  Follow the system's rules to add information for each value one by one (**After filling in a set of name, type, answer, and unit, click "Add New Value", which adds an entry**).
  
  For the name field, fill in the description of the value to be found (later used in the prompt to guide the model's output).

- Multiple Answers per problem

  Follow the system's rules to fill in (**After filling in a set of answers, types, and units, click "Add Answer", which adds an entry**).
  
- Other (Human Evaluation Required)

  Does not fall into the above categories and does not match any of the above answer types, such as writing chemical equations or simple explanation problems (e.g., determining whether a car is accelerating or decelerating). You need to annotate the problem scenario (for later use in large model simulations to guide the model's evaluation), reference answer, and solution (if available).


### 4. Save
All annotated outputs are stored as ./subject/competition_abbreviation/file_name/date_marker.json in the ./output/ folder.
There are three save-related buttons in the annotation interface:
- Save this problem: Temporarily save this problem. You can click save again after modifying the annotation information.
- Save & Next problem: Save this problem and start annotating the next problem. The annotation information of the previous problem will be cleared from the page.
- Save & Next problem (without clearing): Save this problem and start annotating the next problem. The annotation information of the previous problem will remain on the page (this design is to facilitate the annotation of a large problem with multiple sub-problems, where some images and problem stems may be used for several sub-problems).

### 5. Edit Mode
If you have already annotated some content in the current document and want to modify certain previously annotated problems, you can expand the left sidebar.
The sidebar will display all the problems you have annotated in the current document (each problem is displayed with the external save file name + problem content).

Click on the problem you want to modify, and the system will enter "Edit Mode" and load the annotation content of the selected problem in the annotation panel on the right, allowing you to make modifications.

After finishing the modifications, click save to update the annotation for that problem.

Click "Exit Modify Mode" to continue normal annotation.

Click "Delete This problem" to delete the external storage file for that problem.
