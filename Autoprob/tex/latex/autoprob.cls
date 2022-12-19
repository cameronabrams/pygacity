\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{autoprob}[2022/12/15]

\RequirePackage{datatool}
\RequirePackage{graphicx}
\RequirePackage{amsfonts}
\RequirePackage{amssymb}
\RequirePackage{amsmath}
\RequirePackage{latexsym}
\RequirePackage{epic}
\RequirePackage{eepic}
\RequirePackage{multirow}
\RequirePackage[mathscr]{euscript}
\RequirePackage{xcolor}
\RequirePackage{accents}
\RequirePackage{xifthen}
\RequirePackage{xfp}

\newif\ifshowsolutions
\showsolutionsfalse
\newif\ifshowanswers
\showanswersfalse
\newif\ifgivespace
\givespacefalse

\DeclareOption{solutions}{\showsolutionstrue}
\DeclareOption{answers}{\showanwersstrue}
\DeclareOption{givespace}{\givespacetrue}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass{article}

\RequirePackage{cancel}
\RequirePackage{enumitem}

\newsavebox{\fmbox}
\newenvironment{fmpage}[1]
{\begin{lrbox}{\fmbox}\begin{minipage}[c]{#1}}
{\end{minipage}\end{lrbox}\fbox{\usebox{\fmbox}}}

\RequirePackage{listings}
\definecolor{Brown}{cmyk}{0,0.81,1,0.60}
\definecolor{OliveGreen}{cmyk}{0.64,0,0.95,0.40}
\definecolor{CadetBlue}{cmyk}{0.62,0.57,0.23,0}
\definecolor{lightlightgray}{gray}{0.9}
\lstdefinestyle{mybash}{language=bash,basicstyle=\ttfamily\color{white},backgroundcolor=\color{black},numbers=none,keywordstyle=\bf\color{white},showspaces=false,showstringspaces=false}
\lstdefinestyle{myc}{language=C,basicstyle=\ttfamily\color{CadetBlue},backgroundcolor=\color{lightlightgray},frame=none,numbers=none,keywordstyle=\bf\color{CadetBlue},tabsize=2,showspaces=false,showstringspaces=false}
\lstdefinestyle{mypython}{
language=Python,                             % Code langugage
basicstyle=\footnotesize\ttfamily,                   % Code font, Examples: \footnotesize, \ttfamily
keywordstyle=\color{OliveGreen},        % Keywords font ('*' = uppercase)
commentstyle=\color{gray},              % Comments font
numbers=left,                           % Line nums position
numberstyle=\tiny,                      % Line-numbers fonts
stepnumber=1,                           % Step between two line-numbers
numbersep=5pt,                          % How far are line-numbers from code
backgroundcolor=\color{lightlightgray}, % Choose background color
frame=none,                             % A frame around the code
tabsize=4,                              % Default tab size
captionpos=b,                           % Caption-position = bottom
breaklines=true,                        % Automatic line breaking?
breakatwhitespace=false,                % Automatic breaks only at whitespace?
showspaces=false,                       % Dont make spaces visible
showstringspaces=false,
showtabs=false,                         % Dont make tabls visible
numbers=none
%columns=flexible,                       % Column format
}
\newcommand{\inl}[1][]{%
  \lstinline[style=mypython,basicstyle=\ttfamily,#1]%
}

\DeclareRobustCommand{\molar}[1]{\protect\underaccent{\bar}{#1}}
\newcommand{\parmol}[2]{\overline{#1}_{#2}}
\def\Ub{\molar{U}}
\def\Hb{\molar{H}}
\def\Sb{\molar{S}}
\def\Vb{\molar{V}}
\def\Gb{\molar{G}}
\def\thetab{\molar{\theta}}
\newcommand{\dm}[1]{\Delta_{\rm mix} {#1}}
\newcommand{\deriv}[2]{\frac{d{#1}}{d{#2}}}
\newcommand{\pv}{P^{\rm vap}}
\newcommand{\pd}[2]{\frac{\partial {#1}}{\partial {#2}}}
\newcommand{\tpd}[3]{\left(\frac{\partial {#1}}{\partial {#2}}\right)_{#3}}
\newcommand{\ppd}[2]{\frac{\partial^2 {#1}}{\partial {#2}^2}}
\newcommand{\dr}[1]{\Delta_{\rm rxn} {#1}}
\newcommand{\df}[1]{\Delta_{\rm f} {#1}^\circ}
\newcommand{\hr}{\dr{H^{\circ}}}
\newcommand{\gr}{\dr{G^{\circ}}}
\newcommand{\hf}{\df{H}}
\newcommand{\gf}{\df{G}}

\newcommand{\Universityname}{\sc Drexel University}
\newcommand{\Departmentname}{Department of Chemical and Biological Engineering}
\newcommand{\Coursename}{CHE 330 -- Chemical Engineering Thermodynamics II}
\newcommand{\Termname}{Winter 2022-2023}
\newcommand{\Termcode}{202225}
\newcommand{\Instructorname}{Prof. Abrams}
\newcommand{\Instructoremail}{cfa22@drexel.edu}
\newcommand{\Subjectname}{Thermodynamics}
\newcommand{\Solutionscolor}{blue}
\newcommand{\Solutionsheader}{\color{\Solutionscolor}\so{\sc SOLUTIONS}\color{black}}
\newcommand{\Solutionheader}{\color{\Solutionscolor}\so{\sc SOLUTION.}\color{black}}

\newcommand{\plainheader}[1]{
    \begin{centering}
        \Universityname\\
        \Departmentname\\
        \Coursename\ -- \Termname\ (\Termcode)\\*[1em]
        {#1}\\
    \end{centering}
}

\newcommand{\psheader}[3]{
    \begin{centering}
        \Universityname\\
        \Departmentname\\
        \Coursename\ -- \Termname\ (\Termcode)\\
        \Instructorname\ -- \Instructoremail\\
        Problem Set {#1}\ -- Due {#2}\\*[1em]
        \ifshowsolutions
        \Solutionsheader\\
        \fi
    \end{centering}
}

\newcommand{\examheader}[2]{
    \begin{centering}
        \Universityname\\
        \Departmentname\\
        \Coursename\ -- \Termname\ (\Termcode)\\
        \Instructorname\ -- \Instructoremail\\
        {#1}\ -- {#2}\\*[1em]
        \ifshowsolutions
        \Solutionsheader\\
        \fi
        \ifshowsolutions
        \Solutionsheader\\*[1cm]
        \fi
    \end{centering}
}

\newcommand{\qualifierheader}[1]{
    \begin{centering}
        \Universityname\\
        \Departmentname\\
        Ph.D. Qualifying Exam\\
        \Subjectname\\
        {#1}\\*[5mm]
        \ifshowsolutions
        \Solutionsheader\\*[1cm]
        \fi
    \end{centering}
}

\newcommand{\morespace}[1]{
\noindent More space for problem #1
\clearpage
}
\newcommand\examquestion[2]{\givespacetrue\newcommand\totalpoints{#1}\input{#2}\givespacefalse}
\newcommand\qualquestion[2]{\input{#1}\ifgivespace\morespace{#2}\fi}
\newcommand\practicequestion[1]{\givespacefalse\input{#1}}
\newcommand\problem[1]{\input{#1}}

\RequirePackage[version=4]{mhchem}
\RequirePackage{booktabs}
\RequirePackage[font=small,labelfont=bf]{caption}
\RequirePackage{pythontex}
