package com.example.demo;

import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiFile;
import com.jetbrains.python.psi.PyFromImportStatement;
import com.jetbrains.python.psi.PyImportElement;
import com.jetbrains.python.psi.PyImportStatement;
import com.jetbrains.python.psi.PyReferenceExpression;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class ImportsChecker {
    static public List<String> check(PsiFile file){
        List<String> imports = new ArrayList<>();
        for(PsiElement children : file.getChildren()) {
            if (Objects.equals(children.toString(), "PyImportStatement")) {
                PyImportStatement importStatement = (PyImportStatement) children;
                for(PsiElement childrenImportStatement :importStatement.getChildren()) {
                    if (childrenImportStatement.toString().startsWith("PyImportElement")) {
                        PyImportElement importElement = (PyImportElement)childrenImportStatement;
                        if(importElement.getAsName() == null)
                            imports.add(Objects.requireNonNull(importElement.getImportedQName()).toString());
                        else
                            imports.add(Objects.requireNonNull(importElement.getImportedQName()).toString() + "|as|" + Objects.requireNonNull(importElement.getAsName()));

                    }

                }
            }
            if (Objects.equals(children.toString(), "PyFromImportStatement")) {
                PyFromImportStatement importFromStatement = (PyFromImportStatement) children;
                if(importFromStatement.getFullyQualifiedObjectNames().isEmpty()){
                    imports.add(Objects.requireNonNull(importFromStatement.getImportSourceQName()).toString() + "|*");
                }
                else{
                    String lib = null;
                    for(PsiElement childrenImportFromStatement : importFromStatement.getChildren()) {
                        if (childrenImportFromStatement.toString().startsWith("PyReferenceExpression")) {
                            PyReferenceExpression referenceExpression = (PyReferenceExpression) childrenImportFromStatement;
                            lib = referenceExpression.getName();
                        }
                        if (childrenImportFromStatement.toString().startsWith("PyImportElement")) {
                            PyImportElement importElement = (PyImportElement)childrenImportFromStatement;
                            if(lib != null){
                                imports.add(lib + "|" + importElement.getName());
                            }
                        }

                    }
                }
            }
        }
        return imports;
    }
}
