package main

import "fmt"

func main(){
	counter := 0

	channel := make(chan int)

	for {
		fmt.Println("Starting threads")
		go roflThread(channel)
		counter += 1

		channel <- counter
		fmt.Println("Threads active: ", counter)
	}
}

func roflThread(ch chan int){
	test := 0
	for iter := range ch {
		test += iter
		fmt.Println(<- ch)
	}
}