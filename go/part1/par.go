package main

import "fmt"

func main() {
	
	channel := make(chan int)

	fmt.Println("asdf")

	go test1(channel)
	go test2(channel, 5)

	never := make(chan int)
	<- never
}



func test1(ch chan int) {
	test := <- ch
	
	for test >= 0 {
		fmt.Println(test)
		test = <- ch
	}
}

func test2(ch chan int, n int) {
	for i := 0; i < n; i++ {
		fmt.Println("I'm at ", i, " ur zlow...")
		ch <- i
	}
	ch <- -1
}