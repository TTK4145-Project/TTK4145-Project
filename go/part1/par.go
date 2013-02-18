package main

import "fmt"

func main() {
	
	channel := make(chan int)

	fmt.Println("asdf")

	go test1(channel)
	go test2(channel, 5)

	test := 0

	for iter := range channel{
		test += iter
	}
}



func test1(ch chan int) {
	
	for iter := range ch {
		fmt.Println(iter)
	}
}

func test2(ch chan int, n int) {
	for i := 0; i < n; i++ {
		fmt.Println("I'm at ", i, " ur zlow...")
		ch <- i
	}
	ch <- -1
	close (ch)
}