package main
import  "fmt"

func main(){
	fmt.Printf("hello, world\n")

	// variable with var
	var (
		test = 1
		test2 = 2
	)
	fmt.Println(test)
	fmt.Println(test2)

	// variable with :=
	test3 := "HEI!"
	fmt.Println(test3)

	// const
	const (
		test4 = "HÅ"
		test5 = "HA"
	)
	fmt.Println(test4)
	fmt.Println(test5)

	// struct
	type account struct {
		name string
		accnum int
		val float64
	}
	var a = new(account)
	a.name = "Mr. Cake"
	a.accnum = 1234
	a.val = 1336.9
	fmt.Println("Name: ", a.name)
	fmt.Println("Account number: ", a.accnum)
	fmt.Println("Money left: ", a.val)

	// for lup
	for i := 0; i < 10; i++ {
		fmt.Println("For lup: ", i);
	}

	// array
	array := []string{"lorem","ipsum","dolor","sit","amet"}
	fmt.Println("This is my Array: ", array, ". Let's loop through it!")
	for key, val := range array {
		fmt.Println(key,val)
	}
	fmt.Println()

	// loop Q?
	// x and y are key and value to the array

	// there iz no while loopz, only modified/generalizd for lupz (for condition {})
	i := 9001
	for i > 10 {
		fmt.Println("make it cry on its first loop!")
		i = 1
	}

	

	fmt.Println(twoNumbers(123, 543))
}

// a function!
func twoNumbers(x float64, y float64) float64 {
	return x + y
}