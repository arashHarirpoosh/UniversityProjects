import java.io.File;
import java.io.FileNotFoundException;
import java.util.*;

public class convertToChomsky {

    private String readFile(int num, String name){
        String wait = "";
        try {
            File x = new File(num+"\\"+name+".txt");
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

    /**
     * In This Method We Check Whether The String Belong To Variables Or Not
     * @param Var
     * @param g
     * @return
     */
    private boolean isVar(String Var[],String g){
        for (String aVar : Var) {
            if (g.equals(aVar)) {
                return true;
            }
        }
        return false;
    }

    /**
     * In This Method We Remove Product Unit Of A Grammar
     * @param Var Array of Variables
     * @param grammar HashMap of grammar
     * @return The Changed Grammar
     */

    private HashMap<String,ArrayList<String>> removeUnitProduct(String Var[],HashMap<String,ArrayList<String>> grammar){
        String key[] = grammar.keySet().toArray(new String[0]);
        String unitKey;
        ArrayList<String> newValue = new ArrayList<>();
        ArrayList<String> removeUnit = new ArrayList<>();
        char unit = ' ';
        for (String aKey : key) {
            newValue.clear();
            removeUnit.clear();
            for (int j = 0; j < grammar.get(aKey).size(); j++) {
                unit = grammar.get(aKey).get(j).charAt(0);
                unitKey = grammar.get(aKey).get(j);
                if (grammar.get(aKey).get(j).length() == 1 && isVar(Var,String.valueOf(unit) )) {
                        newValue.addAll(grammar.get(unitKey));
                        removeUnit.add(unitKey);
                }
            }
            grammar.get(aKey).addAll(newValue);
            grammar.get(aKey).removeAll(removeUnit);

        }

        return grammar;
    }

    /**
     * In This Method We Check Whether The Grammar Includes Both Variable And Terminals Or Whether Includes Terminals With Length Greater Than one or not.
     * @param Var Array of Variables
     * @param grammar   grammar
     * @return Whether The Grammar Is Complex Or Not
     */
    private boolean isComplex(String Var[],String grammar){
        int terminal = 0,variable = 0;
        for (int i = 0; i < grammar.length(); i++) {
            for (String aVar : Var) {
                if (String.valueOf(grammar.charAt(i)).equals(aVar)) {
                    variable++;
                } else {
                    terminal++;
                }

                if (variable > 0 && terminal > 0 || terminal >1) {
                    return true;
                }
            }

        }
        return false;
    }

    /**
     * In This function we change grammars that have Terminals and Variables
     * @param Var Array of Variables
     * @param grammar HashMap of grammar
     * @return The changed grammar
     */
    private HashMap<String,ArrayList<String>> removeComplexity(String Var[], HashMap<String,ArrayList<String>> grammar){
        HashMap<String,ArrayList<String>> newgrammar = new HashMap<>();
        ArrayList<String> newVal = new ArrayList<>();
        String key[] = grammar.keySet().toArray(new String[0]);
        for (int i = 0; i < grammar.size() ; i++) {
            for (int j = 0; j <grammar.get(key[i]).size() ; j++) {
                if (grammar.get(key[i]).get(j).length() > 1 &&isComplex(Var, String.valueOf(grammar.get(key[i]).get(j)))){
                    for (int k = 0; k <grammar.get(key[i]).get(j).length() ; k++) {
                        if (!isVar(Var, String.valueOf(grammar.get(key[i]).get(j).charAt(k))) ){
                            newVal.add(String.valueOf(grammar.get(key[i]).get(j).charAt(k)));
                            ArrayList<String> value = new ArrayList<>();
                            value.add(String.valueOf(grammar.get(key[i]).get(j).charAt(k)));
                            String newKey = "X" + String.valueOf(newgrammar.size());
                            if (!grammar.containsValue(newVal) && !newgrammar.containsValue(value)) {
                                newgrammar.put(newKey, value);

                            }

                        }
                    }

                }

            }
        }
        for (int i = 0; i <grammar.size() ; i++) {
            for (int j = 0; j <grammar.get(key[i]).size() ; j++) {
                for (int k = 0; k <grammar.get(key[i]).get(j).length() ; k++) {
                    if (!isVar(Var, String.valueOf(grammar.get(key[i]).get(j).charAt(k)))){
                        newVal.add(String.valueOf(grammar.get(key[i]).get(j).charAt(k)));
                        ArrayList<String> value = new ArrayList<>();
                        value.add(String.valueOf(grammar.get(key[i]).get(j).charAt(k)));
                        String newKey[] = newgrammar.keySet().toArray(new String[0]);
                        if (newgrammar.containsValue(value)) {
                            for (String aNewKey : newKey) {
                                if (grammar.get(key[i]).get(j).length()>1) {
                                    grammar.get(key[i]).set(j, grammar.get(key[i]).get(j).replace(newgrammar.get(aNewKey).get(0), aNewKey));
                                }
                            }

                        }

                    }
                }
            }
        }
        grammar.putAll(newgrammar);
        return grammar;
    }

    private int CountVar(String grammar){
        int total = 0;
        for (int i = 0; i <grammar.length() ; i++) {
            if (!Character.isDigit(grammar.charAt(i))){
                total++;
            }
        }
        return total;

    }

    private int lengthOfFirstVar(String grammar){
        int total = 1;
        for (int i = 1; i <grammar.length() ; i++) {
            if (!Character.isDigit(grammar.charAt(i))){
                break;
            }
            total++;
        }
        return total;
    }

    /**
     * In This Method All Variables That They're Length Is More Than Two Will Be Converted To Length Two
     * @param grammar  HashMap of grammar
     * @return The Final Grammar
     */
    private HashMap<String,ArrayList<String>> convertToLengthTwo(HashMap<String,ArrayList<String>> grammar){
        HashMap<String,ArrayList<String>> newgrammar = new HashMap<>();
        String key[];
        for (int i = 0; i < grammar.keySet().size(); i++) {
            key = grammar.keySet().toArray(new String[0]);
            for (int j = 0; j < grammar.get(key[i]).size(); j++) {
                if (CountVar(grammar.get(key[i]).get(j))>2){
                    String gra = grammar.get(key[i]).get(j);
                   if (!newgrammar.containsValue(new ArrayList<String>(Collections.singleton(gra.substring(lengthOfFirstVar(gra)))))) {
                        String newKey = "Y" + String.valueOf(newgrammar.size());
                        newgrammar.put(newKey, new ArrayList<String>(Collections.singleton(gra.substring(lengthOfFirstVar(gra)))));
                        grammar.get(key[i]).set(j, gra.replaceAll(newgrammar.get(newKey).get(0), newKey));
                        grammar.put(newKey, newgrammar.get(newKey));

                   }
                   else {
                       for (int k = 0; k < newgrammar.keySet().size(); k++) {
                           if (newgrammar.get(newgrammar.keySet().toArray(new String[0])[k]).get(0).equals(gra.substring(lengthOfFirstVar(gra)))){
                               grammar.get(key[i]).set(j,gra.replaceAll(newgrammar.get(newgrammar.keySet().toArray(new String[0])[k]).get(0), newgrammar.keySet().toArray(new String[0])[k]));
                               break;

                           }

                       }
                   }
                }
            }
        }

        return grammar;
    }

    public static void main(String[] args) {
        convertToChomsky ctc = new convertToChomsky();
        String[] temp;
        String Var[];
        String ter[];
        HashMap<String,ArrayList<String>> grammar = new HashMap<>();
        String newGrammar[];
        String wait = "";
        Scanner in = new Scanner(System.in);
        Scanner input = new Scanner(System.in);

        System.out.println("Please say the number of the grammar that you want ?");
        int numOfGram = in.nextInt();
        /**
         * Read the variables from the file and put them in an array
         */
        wait = ctc.readFile(numOfGram, "variables");
        Var = new String[wait.length()];
        temp = wait.replace(',', ' ').split("");
        for (int i = 0; i <temp.length ; i++) {
            if (!temp[i].equals(" ")){
                Var[i] = temp[i];

            }
        }

        /**
         * Read the terminals from the file and put them in an array
         */
        wait = ctc.readFile(numOfGram, "terminals");
        ter = new String[wait.length()];
        temp = wait.replace(',', ' ').split("");
        for (int i = 0; i <temp.length ; i++) {
            if (!temp[i].equals(" ")){
                ter[i] = temp[i];
            }
        }
        /**
         * Read the Grammar from the file and put them in a hash map with key the left side of the grammar and value the right side of the grammar
         */
        System.out.println("This is the Grammar that you choose: ");
        try {
            File x = new File("D:\\semester4\\Theory of Machines and Languages\\finalTestCase\\"+numOfGram+"\\grammar.txt");
            Scanner sc = new Scanner(x);
            while(sc.hasNext()) {
                String gra[] = sc.next().split("->");
                grammar.put(gra[0],new ArrayList<>(Arrays.asList(gra[1].replace(";", "").replace("|", " ").split("\\s+"))));
                System.out.print(gra[0] + " -> ");
                for (int i = 0; i <grammar.get(gra[0]).size() ; i++) {
                    System.out.print(grammar.get(gra[0]).get(i)+ " ");
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
        grammar = ctc.convertToLengthTwo(ctc.removeComplexity(Var, ctc.removeUnitProduct(Var, grammar)));
        String newGrammarKey[] = new String[grammar.size()];
        int newGramIndex = 0;
        for (String aVar : Var) {
            if (aVar != null) {
                newGrammarKey[newGramIndex] = aVar;
                newGramIndex++;
            }
        }
        for (int i = 0; i < grammar.size(); i++) {
            boolean var = false;
            for (int j = 0; j < newGramIndex-1; j++) {
               if (grammar.keySet().toArray(new String[0])[i].equals(newGrammarKey[j])){
                   var = true;
                   break;
               }
            }
            if (!var) {
                newGrammarKey[newGramIndex-1] = grammar.keySet().toArray(new String[0])[i];
                newGramIndex++;
            }
        }
        System.out.println("\n"+"Chomsky Form Of The Grammar Is : \n");
        for (String aNewGrammarKey : newGrammarKey) {
            System.out.print(aNewGrammarKey + " --> ");
            for (int j = 0; j < grammar.get(aNewGrammarKey).size(); j++) {
                if (j != grammar.get(aNewGrammarKey).size() - 1) {
                    System.out.print(grammar.get(aNewGrammarKey).get(j) + " | ");
                } else {
                    System.out.print(grammar.get(aNewGrammarKey).get(j));

                }
            }
            System.out.println();
        }

    }
}
