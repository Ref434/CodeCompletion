package com.example.demo;

import com.intellij.codeInsight.completion.*;
import com.intellij.codeInsight.lookup.LookupElement;
import com.intellij.codeInsight.lookup.LookupElementBuilder;
import com.intellij.patterns.PlatformPatterns;
import com.intellij.psi.PlainTextTokenTypes;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiFile;
import com.intellij.psi.PsiRecursiveVisitor;
import com.intellij.util.ProcessingContext;
import com.jetbrains.python.psi.*;
import kotlin.collections.ArrayDeque;
import org.jetbrains.annotations.NotNull;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;
import java.util.*;

public class MyCompletionContributor extends CompletionContributor {
    @Override
    public void fillCompletionVariants(@NotNull CompletionParameters parameters, @NotNull CompletionResultSet result)  {
        super.fillCompletionVariants(parameters, result);
    }



    public MyCompletionContributor() {

        extend(CompletionType.BASIC, PlatformPatterns.psiElement(),
                new MethodCompletionProvider(true));

        extend(CompletionType.BASIC, PlatformPatterns.psiElement(),
                new VariableCompletionProvider(true));
    }

}