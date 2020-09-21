import java.io.File;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.Scanner;
import java.util.Set;

public class stringDetector {
   private String readFile(int num, String name){
        String wait = "";
        try {
            File x = new File("OfficialTests\\OfficialTests\\"+num+"\\"+name+".txt");
            Scanner sc = new Scanner(x);
            while(sc.hasNext()) {
                wait = sc.next();
            }
            sc.close();
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
        }
        return  wait;
    }
    private int CountUpper(String s){
       int upperCase =0;
        for (int k = 0; k < s.length(); k++) {
            // Check for uppercase letters.
            if (Character.isUpperCase(s.charAt(k))){
                upperCase++;
            }
            }
            return upperCase;
        }
        private String findFirstGrammar(Set<String> keys, String word){
            String firstGrammar = "";
            for (String aKey : keys) {
                if (word.contains(aKey)) {
                    firstGrammar = aKey;
                    break;
                }
            }
            return firstGrammar;
        }
    private boolean checkString( HashMap <String,String[]> grammar,String startString, String string ){
       boolean exist = false;

       Set<String> keys = grammar.keySet();
        for (int i = 1; i < startString.length() + 1; i++) {
            for (int j = 0; j < startString.length() - i + 1 ; j++) {
                String subString = startString.substring(j,j+i);
                if (keys.contains(subString)){
                    String gr[] = grammar.get(findFirstGrammar(keys, startString));
                    for (String aGr : gr) {
                        String createdWord;
                        if (aGr.equals("?")) {
                             createdWord = startString.substring(0, j) + startString.substring(j + i);
                        } else {
                            createdWord = startString.substring(0, j) + aGr + startString.substring(j + i);
                            if (gr[gr.length-1].equals("?")){
                                String interval = createdWord.replaceFirst(findFirstGrammar(keys, startString), "");
                                if (interval.equals(string)){
                                    return true;
                                }
                            }
                        }
                        if (createdWord.equals(string)) {
                            exist = true;
                            return true;
                        }
                        if (createdWord.length() <= string.length() + CountUpper(createdWord)) {
                            exist = exist || checkString( grammar, createdWord, string);
                        }
                    }
                }
            }

        }
       return exist;
    }

    public static void main(String[] args) {
        stringDetector stringDetector = new stringDetector();
        char temp[],Var[],ter[];
        HashMap <String,String[]> grammar = new HashMap<>();
        String wait;
        Scanner in = new Scanner(System.in);
        Scanner input = new Scanner(System.in);


        System.out.println("Please say the number of the grammar that you want ?");
        int numOfGram = in.nextInt();
        /**
         * Read the variables from the file and put them in an array
         */
        wait = stringDetector.readFile(numOfGram, "variables");
        Var = new char[wait.length()];
        temp = wait.replace(',', ' ').toCharArray();
        for (int i = 0; i <temp.length ; i++) {
            if (temp[i] !=' '){
                Var[i] = temp[i];
            }
        }

        /**
         * Read the terminals from the file and put them in an array
         */
        wait = stringDetector.readFile(numOfGram, "terminals");
        ter = new char[wait.length()];
        temp = wait.replace(',', ' ').toCharArray();
        for (int i = 0; i <temp.length ; i++) {
            if (temp[i] !=' '){
                ter[i] = temp[i];
            }
        }
        /**
         * Read the Grammar from the file and put them in a hash map with key the left side of the grammar and value the right side of the grammar
         */
        System.out.println("This is the Grammar that you choose: ");
        try {
            File x = new File("D:\\F(for programming)\\Java Work Space\\grammerDetector\\" +
                    "OfficialTests\\OfficialTests\\"+numOfGram+"\\grammar.txt");
            Scanner sc = new Scanner(x);
            while(sc.hasNext()) {
                String gra[] = sc.next().split("->");
                grammar.put(gra[0],gra[1].replace(";", "").replace("|", " ").split("\\s+"));
                System.out.print(gra[0] + " -> ");
                for (int i = 0; i <grammar.get(gra[0]).length ; i++) {
                    System.out.print(grammar.get(gra[0])[i]+ " ");
                }
                System.out.println();
            }
            sc.close();
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
        }
        /**
         * Get the string from user
         */
        System.out.println("Please write the string that you want : ");
        System.out.println(stringDetector.checkString(grammar, "S",input.nextLine() ));

    }
}
