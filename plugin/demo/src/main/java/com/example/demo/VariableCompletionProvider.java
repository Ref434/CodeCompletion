package com.example.demo;

import com.intellij.codeInsight.completion.CompletionParameters;
import com.intellij.codeInsight.completion.CompletionProvider;
import com.intellij.codeInsight.completion.CompletionResultSet;
import com.intellij.codeInsight.lookup.LookupElement;
import com.intellij.codeInsight.lookup.LookupElementBuilder;
import com.intellij.psi.PsiFile;
import com.intellij.ui.JBColor;
import com.intellij.util.PlatformIcons;
import com.intellij.util.ProcessingContext;
import org.jetbrains.annotations.NotNull;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

class VariableCompletionProvider extends CompletionProvider<CompletionParameters> {
    private final boolean onlyManual;

    private static final String USER_AGENT = "Mozilla/5.0";

    private static String sendGET(String variable, String imports) throws IOException {
        String GET_URL = "http://localhost:7000/" + variable + "/" + imports;
        URL obj = new URL(GET_URL);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        con.setRequestMethod("GET");
        con.setRequestProperty("User-Agent", USER_AGENT);
        int responseCode = con.getResponseCode();
        System.out.println("GET Response Code :: " + responseCode);
        if (responseCode == HttpURLConnection.HTTP_OK) { // success
            BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
            String inputLine;
            StringBuffer response = new StringBuffer();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            // print result
            return response.toString();
        } else {
            return "GET request did not work.";
        }
    }


    VariableCompletionProvider(boolean onlyManual) {
        this.onlyManual = onlyManual;
    }

    public void addCompletions(@NotNull CompletionParameters parameters,
                               @NotNull ProcessingContext context,
                               @NotNull CompletionResultSet resultSet) {


        // return early if we're not supposed to show items
        // in the automatic popup
        if (parameters.isAutoPopup() && onlyManual) {
            return;
        }

        String prefix = resultSet.getPrefixMatcher().getPrefix();
        if (prefix.isEmpty()) {
            return;
        }

        List<String> importsLib = new ArrayList<>();
        PsiFile file = parameters.getOriginalFile();
        List<String> imports = ImportsChecker.check(file);

        String[] suggestions;
        for(String element: imports){
            importsLib.add(element.split("\\|")[0].split("\\.")[0]);
        }

        try {
            String answer = sendGET(prefix,importsLib.toString());
            if (answer.startsWith("Unable to get method completion")) {
                suggestions = answer.replace("Unable to get method completion | [", "").replace("]", "").replaceAll("'", "").split(", ");
                for (String suggestion : suggestions) {
                    LookupElement e = LookupElementBuilder.create(suggestion + " =")
                            .withPresentableText(suggestion)
                            .withItemTextForeground(JBColor.YELLOW)
                            .bold()
                            .withIcon(PlatformIcons.VARIABLE_ICON);
                    resultSet.addElement(e);
                }
            }
            resultSet.stopHere();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

    }



}